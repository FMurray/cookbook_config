from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
import urllib.parse

from databricks.sdk import WorkspaceClient


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
    permissions: Optional[dict] = Field(default=None)
    details: Optional[dict] = Field(default=None)
    workspace_link: Optional[str] = Field(default=None)

    def generate_workspace_link(self, db_client: WorkspaceClient):
        host = db_client.config.host
        volume_path = (
            f"/Volumes/{self.catalog}/{self.schema}/{self.volume_name}/{self.path}"
        )
        encoded_volume_path = urllib.parse.quote(volume_path)
        workspace_id = db_client.get_workspace_id()
        return f"{host}/explore/data/volumes/{self.catalog}/{self.schema}/{self.volume_name}?o={workspace_id}&volumePath={encoded_volume_path}"

    def fetch_details(self, db_client: WorkspaceClient):
        try:
            self.details = db_client.volumes.read(
                f"{self.catalog}.{self.schema}.{self.volume_name}"
            )
            self.workspace_link = self.generate_workspace_link(db_client)
        except Exception as e:
            raise ValueError(f"Failed to fetch volume details: {e}")
        return self.details

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
