import pathlib
import anywidget
import traitlets
import yaml
from typing import Dict, List, TypedDict

from pydantic_settings import BaseSettings
from databricks.sdk import WorkspaceClient
from ai_cookbook.pipeline.pipeline import Pipeline


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
        self.observe(self.on_edges_change, names="edges")

    def on_edges_change(self, change):
        print(f"Edges changed: {change}")

    def populate_data(self, client: WorkspaceClient):
        """Populate the widget with the pipeline configuration"""

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
                if isinstance(value, str):
                    if "." in value:
                        parts = value.split(".")
                        if len(parts) == 3:
                            catalogs.add(parts[0])
                            schemas.add(parts[1])
                            tables.add(parts[2])
                        elif len(parts) == 2:
                            schemas.add(parts[0])
                            tables.add(parts[1])

        # Update the traits
        self.catalogs = sorted(list(catalogs))
        self.schemas = sorted(list(schemas))
        self.tables = sorted(list(tables))
