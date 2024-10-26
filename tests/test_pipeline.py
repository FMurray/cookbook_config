import pytest
from src.pipeline.pipeline import Pipeline
from src.pipeline.data_source import DataSource
from src.pipeline.processing_step import ProcessingStep
from src.pipeline.output import Output
from pydantic import ValidationError

source_1 = DataSource(
    name="source1",
    catalog="test_catalog",
    schema="test_schema",
    table="test_table",
    type="volume",
    path="/path/to/data",
    format="csv",
)

step_1 = ProcessingStep(
    name="step1",
    function="src.functions.parsing.extract_text_from_pdf",
    inputs=[source_1],
    output_table="output_table1",
)

step_2 = ProcessingStep(
    name="step2",
    function="src.functions.parsing.extract_text_from_pdf",
    inputs=[step_1],
    output_table="output_table2",
)

output_1 = Output(
    name="output1",
    inputs=[step_2],
    type="vector_index",
    embedding_model="openai-embedding-model",
    output_table="output_index",
)


def test_pipeline_successful_initialization(sample_valid_pipeline):
    pipeline = sample_valid_pipeline
    # Assert
    assert len(pipeline.data_sources) == 1
    assert len(pipeline.processing_steps) == 2


def test_pipeline_initialization_missing_required_field():
    # Arrange & Act & Assert
    with pytest.raises(ValidationError):
        DataSource(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
        )


def test_pipeline_initialization_empty_config():
    # Arrange
    empty_config = {}

    # Act & Assert
    with pytest.raises(ValidationError):
        Pipeline(**empty_config)


def test_pipeline_initialization_none_config():
    # Arrange & Act & Assert
    with pytest.raises(TypeError):
        Pipeline(None)


def test_pipeline_is_mutable():
    source_2 = DataSource(
        name="source2",
        catalog="test_catalog",
        schema="test_schema",
        table="test_table",
        type="volume",
        path="/path/to/data",
        format="csv",
    )
    pipeline = Pipeline(
        data_sources=[source_1],
        processing_steps=[step_1, step_2],
        outputs=[output_1],
    )
    pipeline.data_sources.append(source_2)
    assert len(pipeline.data_sources) == 2


def test_pipeline_dag_valid_linear(sample_valid_pipeline):
    pipeline = sample_valid_pipeline
    assert pipeline.execution_order == ["source1", "step1", "step2", "output_output1"]


def test_pipeline_dag_invalid_linear():
    with pytest.raises(ValueError) as exc_info:
        Pipeline(
            data_sources=[source_1],
            processing_steps=[step_1, step_2, step_2],
            outputs=[output_1],
        )
    assert "Duplicate" in str(exc_info.value)


def test_pipeline_dag_invalid_cyclic():
    # Create local instances of steps to form a cycle
    local_step_1 = ProcessingStep(
        name="step1",
        function="src.functions.parsing.extract_text_from_pdf",
        inputs=[source_1],  # Initially points to source_1
        output_table="output_table1",
    )

    local_step_2 = ProcessingStep(
        name="step2",
        function="src.functions.parsing.extract_text_from_pdf",
        inputs=[local_step_1],
        output_table="output_table2",
    )

    # Create the cycle by making step_1 depend on step_2
    local_step_1.inputs = [local_step_2]

    local_output = Output(
        name="output1",
        inputs=[local_step_2],
        type="vector_index",
        embedding_model="openai-embedding-model",
        output_table="output_index",
    )

    # Let's add some debug prints
    print(f"Step 1 inputs: {[x.name for x in local_step_1.inputs]}")
    print(f"Step 2 inputs: {[x.name for x in local_step_2.inputs]}")

    with pytest.raises(ValueError) as exc_info:
        Pipeline(
            data_sources=[source_1],
            processing_steps=[local_step_1, local_step_2],
            outputs=[local_output],
        )
    assert "Cycle" in str(exc_info.value)


@pytest.fixture
def sample_valid_pipeline():
    return Pipeline(
        data_sources=[source_1],
        processing_steps=[step_1, step_2],
        outputs=[output_1],
    )
