from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Union
import re


class DataSourceConfig(BaseModel):
    name: str
    type: str
    path: str
    format: str
    catalog: str
    table_schema: str
    table: str

    @field_validator("type")
    def validate_type(cls, v):
        if v not in {"volume", "database", "api"}:
            raise ValueError(f"Invalid data source type: {v}")
        return v

    @field_validator("table")
    def validate_table_name(cls, v):
        if not re.match(r"^\w+$", v):
            raise ValueError(f"Invalid table name: {v}")
        return v


class ProcessingStepConfig(BaseModel):
    name: str
    function: str
    inputs: List[str]
    output_table: str
    parameters: Optional[dict] = Field(default_factory=dict)

    @field_validator("function")
    def validate_function_exists(cls, v):
        # Assume functions are available in src.functions
        from src.functions import __dict__ as functions_dict

        if v not in functions_dict:
            raise ValueError(f"Function '{v}' does not exist in src.functions")
        return v


class OutputConfig(BaseModel):
    name: str
    type: str
    inputs: List[str]
    embedding_model: str
    output_table: str

    @field_validator("type")
    def validate_type(cls, v):
        if v != "vector_index":
            raise ValueError(f"Invalid output type: {v}")
        return v


class PipelineConfig(BaseModel):
    data_sources: List[DataSourceConfig]
    processing_steps: List[ProcessingStepConfig]
    outputs: List[OutputConfig]
