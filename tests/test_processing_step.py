import pytest

from ai_cookbook.pipeline.processing_step import ProcessingStep
from ai_cookbook.pipeline.data_source import DataSource

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

step_2 = ProcessingStep(
    name="step2",
    function="ai_cookbook.functions.parsing.extract_text_from_pdf",
    inputs=[step_1],
    output_table="output_table2",
)


def test_processing_step():
    pass
