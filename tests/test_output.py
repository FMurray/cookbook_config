import pytest
from ai_cookbook.pipeline.output import Output
from ai_cookbook.pipeline.processing_step import ProcessingStep
from ai_cookbook.pipeline.data_source import DataSource
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
    function="ai_cookbook.functions.parsing.extract_text_from_pdf",
    inputs=[source_1],
    output_table="output_table1",
)


def test_valid_output_creation():
    """Test creating a valid Output instance"""
    output = Output(
        name="test_index",
        type="vector_index",
        inputs=[step_1],
        embedding_model="openai",
        output_table="test_table",
    )

    assert output.name == "test_index"
    assert output.type == "vector_index"
    assert output.inputs[0].name == "step1"
    assert output.embedding_model == "openai"
    assert output.output_table == "test_table"


def test_invalid_type():
    """Test that invalid type raises ValidationError"""
    with pytest.raises(ValidationError) as exc_info:
        Output(
            name="test_index",
            type="invalid_type",
            inputs=[step_1],
            embedding_model="openai",
            output_table="test_table",
        )

    assert "Invalid output type" in str(exc_info.value)


def test_missing_required_fields():
    """Test that missing required fields raise ValidationError"""
    with pytest.raises(ValidationError):
        Output(
            name="test_index",
            type="vector_index",
            # missing required fields
        )


def test_empty_inputs_list():
    """Test creation with empty inputs list"""
    output = Output(
        name="test_index",
        type="vector_index",
        inputs=[],
        embedding_model="openai",
        output_table="test_table",
    )

    assert output.inputs == []


def test_input_types():
    """Test that all fields have correct types"""
    with pytest.raises(ValidationError):
        Output(
            name=123,  # should be string
            type="vector_index",
            inputs=["input1"],
            embedding_model="openai",
            output_table="test_table",
        )

    with pytest.raises(ValidationError):
        Output(
            name="test_index",
            type="vector_index",
            inputs="not_a_list",  # should be list
            embedding_model="openai",
            output_table="test_table",
        )
