from pydantic import BaseModel, ValidationError, field_validator
from typing import Optional
import re


class DataSource(BaseModel):
    name: str
    type: str
    path: str
    format: str
    catalog: str
    schema: str
    volume_name: Optional[str] = None
    table_schema: Optional[str] = None
    table: Optional[str] = None

    @field_validator("type")
    def validate_type(cls, v):
        if v not in {"volume", "delta"}:
            raise ValueError(f"Invalid data source type: {v}")
        return v

    @field_validator("table")
    def validate_table_name(cls, v, info):
        # Skip validation if type is 'volume'
        if info.data.get("type") == "volume":
            return None

        # For 'delta' type, table is required and must be validated
        if v is None:
            raise ValueError("Table name is required for delta source type")
        if not re.match(r"^\w+$", v):
            raise ValueError(f"Invalid table name: {v}")
        return v

    @field_validator("table_schema")
    def validate_table_schema(cls, v, info):
        # Skip validation if type is 'volume'
        if info.data.get("type") == "volume":
            return None

        # For 'delta' type, table_schema is required
        if v is None:
            raise ValueError("Table schema is required for delta source type")
        return v
