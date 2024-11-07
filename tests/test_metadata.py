import pytest
from datetime import datetime
from ai_cookbook.metadata.manager import MetadataManager, Run

from ai_cookbook.pipeline.data_source import DataSource
from ai_cookbook.pipeline.processing_step import ProcessingStep
from ai_cookbook.pipeline.output import Output
from ai_cookbook.pipeline.pipeline import Pipeline


def test_run_creation():
    """Test that Run objects are created with correct attributes"""
    run = Run("test-run-id")

    assert run.run_id == "test-run-id"
    assert isinstance(run.start_time, datetime)


def test_metadata_manager_initialization():
    """Test that MetadataManager initializes with empty collections"""
    manager = MetadataManager()

    assert manager.step_metadata == {}


def test_update_step_metadata():
    """Test updating step metadata with new entries"""
    manager = MetadataManager()

    # Create a mock step object
    class MockStep:
        def __init__(self, name):
            self.name = name

    step = MockStep("test_step")
    run = manager.start_run()

    # Test first update
    manager.update_step_metadata(step, run, "completed")
    metadata = manager.get_metadata(run)
    assert "test_step" in metadata
    assert len(metadata["test_step"]) == 1
    assert metadata["test_step"][0] == "completed"

    # Test second update to same step
    manager.update_step_metadata(step, run, "failed")
    metadata = manager.get_metadata(run)
    assert len(metadata["test_step"]) == 2
    assert metadata["test_step"] == ["completed", "failed"]


def test_get_metadata():
    """Test retrieving metadata"""
    manager = MetadataManager()

    # Create a mock step object
    class MockStep:
        def __init__(self, name):
            self.name = name

    step1 = MockStep("step1")
    step2 = MockStep("step2")
    run = manager.start_run()

    # Add some test data
    manager.update_step_metadata(step1, run, "completed")
    manager.update_step_metadata(step2, run, "failed")

    metadata = manager.get_metadata(run)

    assert len(metadata) == 2
    assert "step1" in metadata
    assert "step2" in metadata
    assert metadata["step1"] == ["completed"]
    assert metadata["step2"] == ["failed"]


def test_start_run():
    """Test starting a new run"""
    manager = MetadataManager()

    run = manager.start_run()

    assert isinstance(run, Run)
    assert isinstance(run.run_id, str)
    assert isinstance(run.start_time, datetime)


def test_record_failed_step():
    """Test recording a failed step"""

    source_1 = DataSource(
        name="source1",
        catalog="test_catalog",
        schema="test_schema",
        table="test_table",
        type="volume",
        path="/path/to/data",
        format="csv",
    )

    def test_function(inputs):
        raise Exception("Test exception")

    step_1 = ProcessingStep(
        name="step1",
        function=test_function,
        inputs=[source_1],
        output_table="output_table1",
    )

    output_1 = Output(
        name="output1",
        inputs=[step_1],
        type="vector_index",
        embedding_model="openai-embedding-model",
        output_table="output_index",
    )

    pipeline = Pipeline(
        data_sources=[source_1],
        processing_steps=[step_1],
        outputs=[output_1],
    )

    run = pipeline.run()

    manager = pipeline.metadata_manager

    # Record the failed step
    # manager.update_step_metadata(step_1, run, "failed")

    # Get metadata for this specific run
    run_metadata = manager.get_metadata(run)

    # Verify the step exists in the run metadata
    assert "step1" in run_metadata

    # Verify the status history for this step
    step_statuses = run_metadata["step1"]
    assert len(step_statuses) == 2
    assert step_statuses[1] == "failed"
