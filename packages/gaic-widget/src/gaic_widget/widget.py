import pathlib
import anywidget
import traitlets
import yaml
from typing import Dict, List, TypedDict
import logging

from pydantic_settings import BaseSettings
from databricks.sdk import WorkspaceClient
from ai_cookbook.pipeline.pipeline import Pipeline
from ai_cookbook.logging.logger import log

# Suppress watchfiles debug logs
logging.getLogger("watchfiles").setLevel(logging.WARNING)


class DatabricksSettings(BaseSettings):
    databricks_host: str


bundler_output_dir = pathlib.Path(__file__).parent / "static"


class Edge(TypedDict):
    source: str
    target: str
    id: str


class ConfigWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static/app.js"
    _css = pathlib.Path(__file__).parent / "static/app.css"

    # Simple list traits
    catalogs = traitlets.List([]).tag(sync=True)
    schemas = traitlets.List([]).tag(sync=True)
    tables = traitlets.List([]).tag(sync=True)

    # Pipeline component traits
    data_sources = traitlets.List(
        traitlets.Dict().tag(sync=True), default_value=[]
    ).tag(sync=True)
    processing_steps = traitlets.List(
        traitlets.Dict().tag(sync=True), default_value=[]
    ).tag(sync=True)
    outputs = traitlets.List(traitlets.Dict().tag(sync=True), default_value=[]).tag(
        sync=True
    )
    edges = traitlets.List(traitlets.Dict().tag(sync=True), default_value=[]).tag(
        sync=True
    )

    def _repr_mimebundle_(self, **kwargs):
        """Ensure proper widget representation in notebooks"""
        return super()._repr_mimebundle_(**kwargs)

    def __init__(self, config_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings = DatabricksSettings(
            databricks_host="https://e2-demo-field-eng.cloud.databricks.com"
        )
        self.client = WorkspaceClient(
            host=self.settings.databricks_host, profile="field-eng"
        )
        self.current_user = self.client.current_user.me()

        # Base configuration traits
        self.display_name = traitlets.Unicode(
            f"GAIC Config Widget - {self.current_user.display_name}"
        ).tag(sync=True)

        self.pipeline = Pipeline.from_yaml(config_path)

        self.populate_data(self.client)
        self.on_msg(self._handle_schema_request)
        self.on_msg(self._handle_volume_request)
        self.on_msg(self._handle_save_source)

    def populate_data(self, client: WorkspaceClient):
        """Populate the widget with the pipeline configuration"""

        log.debug("Populating data")

        for ds in self.pipeline.data_sources:
            ds.fetch_details(client)

        # Extract pipeline components with dynamic attributes
        self.data_sources = [
            {
                "id": ds.name,
                "type": "source",
                "label": ds.name,
                **{
                    k: str(v)
                    for k, v in ds.model_dump().items()
                    if k not in ["name", "type"]
                },
            }
            for ds in self.pipeline.data_sources
        ]

        self.processing_steps = [
            {
                "id": step.name,
                "type": "step",
                "label": step.name,
                "operation": step.operation if hasattr(step, "operation") else "",
                "parameters": {
                    k: str(v) if not isinstance(v, (dict, list)) else v
                    for k, v in step.model_dump().items()
                    if k not in ["name", "type", "inputs"]
                },
            }
            for step in self.pipeline.processing_steps
        ]

        self.outputs = [
            {
                "id": f"output_{output.name}",
                "type": "output",
                "label": output.name,
                **{
                    k: str(v) if not isinstance(v, (dict, list)) else v
                    for k, v in output.model_dump().items()
                    if k not in ["name", "type", "inputs"]
                },
            }
            for output in self.pipeline.outputs
        ]

        # Create edges list with unique IDs
        edges = []
        # Add edges from data sources to processing steps
        for step in self.pipeline.processing_steps:
            for input_step in step.inputs:
                edges.append(
                    {
                        "id": f"edge-{input_step.name}-{step.name}",
                        "source": input_step.name,
                        "target": step.name,
                    }
                )

        # Add edges from processing steps to outputs
        for output in self.pipeline.outputs:
            for input_step in output.inputs:
                edges.append(
                    {
                        "id": f"edge-{input_step.name}-output_{output.name}",
                        "source": input_step.name,
                        "target": f"output_{output.name}",
                    }
                )

        self.edges = edges

        # Extract unique entities from all components
        catalogs = set()
        schemas = set()
        tables = set()

        # Process all components to extract catalog/schema/table info
        for component in [*self.data_sources, *self.processing_steps, *self.outputs]:
            # Look for catalog/schema/table in any field
            for key, value in component.items():
                if key == "catalog":
                    catalogs.add(value)
                elif key == "schema":
                    schemas.add(value)
                elif key == "table":
                    tables.add(value)

        # Update the traits
        self.catalogs = sorted(list(catalogs))
        self.schemas = sorted(list(schemas))
        self.tables = sorted(list(tables))

    def _handle_schema_request(self, _, content, buffers):
        log.debug(f"Received custom message: {content}")
        if content.get("type") == "catalog_selected":
            catalog_name = content.get("catalog")
            if catalog_name:
                catalog_schemas = self.client.schemas.list(catalog_name)
                schema_list = [schema.name for schema in catalog_schemas]
                print(f"Fetched schemas for catalog {catalog_name}: {schema_list}")
                self.send({"type": "schema_update", "schemas": schema_list})

    def _handle_volume_request(self, _, content, buffers):
        if content.get("type") == "volume_request":
            catalog_name = content.get("catalog")
            schema_name = content.get("schema")
            if catalog_name and schema_name:
                try:
                    volumes = self.client.volumes.list(catalog_name, schema_name)
                    volume_list = [volume.name for volume in volumes]
                    log.debug(
                        f"Fetched volumes for {catalog_name}.{schema_name}: {volume_list}"
                    )
                    self.send({"type": "volume_update", "volumes": volume_list})
                except Exception as e:
                    log.error(f"Error fetching volumes: {str(e)}")
                    self.send({"type": "volume_update", "volumes": [], "error": str(e)})

    def _handle_save_source(self, _, content, buffers):
        if content.get("type") == "save_source_node":
            source_data = content.get("data")
            print(f"Saving source node data: {source_data}")

            # Create a new list of data sources
            updated_sources = self.data_sources[:]  # Create a copy

            # Find and update the source
            source_index = next(
                (
                    i
                    for i, ds in enumerate(updated_sources)
                    if ds["id"] == source_data["label"]
                ),
                None,
            )

            if source_index is not None:
                # Create updated source with new values
                updated_source = updated_sources[source_index].copy()
                changes = {}

                for key, new_value in source_data.items():
                    if key in updated_source and updated_source[key] != new_value:
                        changes[key] = {"old": updated_source[key], "new": new_value}
                        updated_source[key] = new_value

                # Replace the old source with the updated one
                updated_sources[source_index] = updated_source

                # Assign the new list to trigger sync
                self.data_sources = updated_sources

                log.debug(f"Source node changes: {changes}")

                # Send confirmation back to UI
                self.send(
                    {
                        "type": "save_confirmation",
                        "status": "success",
                        "message": "Source node saved successfully",
                    }
                )
