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

    settings = DatabricksSettings(
        databricks_host="https://e2-demo-field-eng.cloud.databricks.com"
    )
    workspace = WorkspaceClient(host=settings.databricks_host, profile="field-eng")
    current_user = workspace.current_user.me()

    # New traits for configuration data
    display_name = traitlets.Unicode(
        f"GAIC Config Widget - {current_user.display_name}"
    ).tag(sync=True)
    catalogs = traitlets.List([]).tag(sync=True)
    schemas = traitlets.List([]).tag(sync=True)
    tables = traitlets.List([]).tag(sync=True)

    # Add new traits for pipeline components
    data_sources = traitlets.List([]).tag(sync=True)
    processing_steps = traitlets.List([]).tag(sync=True)
    outputs = traitlets.List([]).tag(sync=True)
    edges = traitlets.List(
        traitlets.Dict(
            per_key_traits={
                "id": traitlets.Unicode(),
                "source": traitlets.Unicode(),
                "target": traitlets.Unicode(),
            },
        ).tag(sync=True),
        default_value=[],
    ).tag(sync=True)

    def __init__(self, config_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_config(config_path)
        self.observe(self.on_edges_change, names="edges")

    def on_edges_change(self, change):
        print(f"Edges changed: {change}")

    def load_config(self, config_path: str):
        """Load and parse the pipeline configuration file"""
        # Create Pipeline instance
        pipeline = Pipeline.from_yaml(config_path)

        # Extract pipeline components
        self.data_sources = [
            {"id": ds.name, "type": "source", "label": ds.name}
            for ds in pipeline.data_sources
        ]

        self.processing_steps = [
            {"id": step.name, "type": "step", "label": step.name}
            for step in pipeline.processing_steps
        ]

        self.outputs = [
            {"id": f"output_{output.name}", "type": "output", "label": output.name}
            for output in pipeline.outputs
        ]

        # Create edges list with unique IDs
        edges = []
        # Add edges from data sources to processing steps
        for idx, step in enumerate(pipeline.processing_steps):
            for input_step in step.inputs:
                edges.append(
                    {
                        "id": f"edge-{input_step.name}-{step.name}",
                        "source": input_step.name,
                        "target": step.name,
                    }
                )

        # Add edges from processing steps to outputs
        for idx, output in enumerate(pipeline.outputs):
            for input_step in output.inputs:
                edges.append(
                    {
                        "id": f"edge-{input_step.name}-output_{output.name}",
                        "source": input_step.name,
                        "target": f"output_{output.name}",
                    }
                )

        self.edges = edges

        # Extract unique entities
        catalogs = set()
        schemas = set()
        tables = set()

        # Process data sources
        for source in self.data_sources:
            if "catalog" in source:
                catalogs.add(source["catalog"])
            if "schema" in source:
                schemas.add(source["schema"])

        # Process processing steps
        for step in self.processing_steps:
            if "output_table" in step:
                table_parts = step["output_table"].split(".")
                if len(table_parts) == 2:
                    schemas.add(table_parts[0])
                    tables.add(table_parts[1])

        # Process outputs
        for output in self.outputs:
            if "output_table" in output:
                table_parts = output["output_table"].split(".")
                if len(table_parts) == 3:
                    catalogs.add(table_parts[0])
                    schemas.add(table_parts[1])
                    tables.add(table_parts[2])

        # Update the traits
        self.catalogs = sorted(list(catalogs))
        self.schemas = sorted(list(schemas))
        self.tables = sorted(list(tables))
