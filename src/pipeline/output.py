from pydantic import ValidationError, BaseModel, field_validator
from typing import List

from src.logging.logger import log
from src.pipeline.processing_step import ProcessingStep


class Output(BaseModel):
    name: str
    type: str
    inputs: List[ProcessingStep]
    embedding_model: str
    output_table: str

    @field_validator("type")
    def validate_type(cls, v):
        if v != "vector_index":
            raise ValueError(f"Invalid output type: {v}")
        return v
