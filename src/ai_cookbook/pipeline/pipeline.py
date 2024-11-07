from typing import List, Dict, Any, Union
import yaml  # Add this import
from pydantic import ValidationError, BaseModel, InstanceOf, model_validator
import importlib
from functools import partial
import time

from ai_cookbook.pipeline.data_source import DataSource
from ai_cookbook.pipeline.processing_step import ProcessingStep
from ai_cookbook.pipeline.output import Output
from ai_cookbook.logging import console
from ai_cookbook.logging.logger import log

from ai_cookbook.metadata.manager import MetadataManager, Run
from ai_cookbook.pipeline.vectorsearch import get_or_create_vector_index
from ai_cookbook.pipeline.ingestion import ingest_volume
from ai_cookbook.pipeline.intermediate_result import write_intermediate_result
from .validation import check_permissions
from .dag import Edge, topological_sort, detect_cycles
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn


class Pipeline(BaseModel):
    data_sources: List[DataSource]
    processing_steps: List[ProcessingStep]
    outputs: List[Output]
    nodes: Dict[str, Union[DataSource, ProcessingStep, Output]] = {}
    edges: List[InstanceOf[Edge]] = []
    execution_order: List[str] = []
    metadata_manager: InstanceOf[MetadataManager] = None
    data_store: Dict[str, Any] = {}

    # @model_validator(mode="before")
    # def generate_ingestion_steps(cls, values):
    #     data_sources = values.get("data_sources", [])
    #     processing_steps = values.get("processing_steps", [])

    #     # Create a mapping of names to objects
    #     name_to_obj = {ds.name: ds for ds in data_sources}

    #     # Collect new ingestion steps
    #     ingestion_steps = []

    #     for ds in data_sources:
    #         if cls._needs_ingestion(ds):
    #             ingestion_step = cls._create_ingestion_step(ds)
    #             ingestion_steps.append(ingestion_step)
    #             name_to_obj[ingestion_step.name] = ingestion_step

    #             # Update processing steps that depend on this data source
    #             for step in processing_steps:
    #                 for idx, input_item in enumerate(step.inputs):
    #                     if input_item == ds:
    #                         step.inputs[idx] = ingestion_step

    #     # Prepend ingestion steps to processing steps
    #     values["processing_steps"] = ingestion_steps + processing_steps

    #     return values

    # @classmethod
    # def _needs_ingestion(cls, data_source):
    #     # Determine if ingestion is needed (e.g., based on type and format)
    #     return data_source.type == "volume"

    # @classmethod
    # def _create_ingestion_step(cls, data_source: DataSource) -> ProcessingStep:
    #     def ingestion_function(inputs):
    #         print(
    #             f"Ingesting data from {data_source.path} into Delta table {data_source.table}"
    #         )
    #         # TODO: Implement ingestion logic
    #         return "ingestion_result"

    #     # Ensure we always have a valid output_table string
    #     if data_source.type == "volume":
    #         output_table = f"{data_source.catalog}.{data_source.schema}.{data_source.volume_name}_raw"
    #     else:
    #         # Provide a default format when not a volume type
    #         output_table = f"{data_source.catalog}.{data_source.schema}.{data_source.table or data_source.name}"

    #     log.info(output_table)

    #     ingestion_step = ProcessingStep(
    #         name=f"ingest_{data_source.name}",
    #         function=ingestion_function,
    #         inputs=[data_source],
    #         output_table=output_table,  # This should now always have a valid string value
    #     )
    #     return ingestion_step

    def model_post_init(self, __context):
        try:
            self.nodes, self.edges = self._build_dag()
            self.execution_order = topological_sort(self.nodes, self.edges)
            for edge in self.edges:
                edge.function = self._determine_edge_function(
                    edge.source, edge.destination
                )
        except ValueError as e:
            log.error(e)
            raise

        self.metadata_manager = MetadataManager()

    def _determine_edge_function(self, source, destination):
        if isinstance(source, DataSource) and source.type == "volume":
            return partial(ingest_volume, source, destination)
        elif isinstance(destination, Output) and destination.type == "vector_index":
            return partial(get_or_create_vector_index, source, destination)
        elif isinstance(source, ProcessingStep) and isinstance(
            destination, ProcessingStep
        ):
            return partial(write_intermediate_result, source, destination)
        else:
            return None

    def _get_incoming_edges(self, node):
        incoming_edges = []
        for edge in self.edges:
            if edge.destination.name == node:
                incoming_edges.append(edge)
        return incoming_edges

    def _build_dag(self):
        nodes = {}
        edges = []
        errors = []

        try:
            # First, build all nodes
            # Add data sources to nodes
            for ds in self.data_sources:
                if ds.name in nodes:
                    errors.append(f"Duplicate data source name: {ds.name}")
                else:
                    nodes[ds.name] = ds

            # Add processing steps to nodes
            for step in self.processing_steps:
                if step.name in nodes:
                    errors.append(f"Duplicate processing step name: {step.name}")
                else:
                    nodes[step.name] = step

            # Add output nodes
            for output in self.outputs:
                nodes[output.name] = output

            # Then, validate all edges
            # Add processing step edges
            for step in self.processing_steps:
                for input_step in step.inputs:
                    input_name = (
                        input_step.name
                        if isinstance(input_step, ProcessingStep)
                        else input_step.name
                    )
                    if input_name not in nodes:
                        errors.append(
                            f"Input {input_name} not found in data sources or processing steps"
                        )
                    else:
                        edges.append(Edge(source=input_step, destination=step))

            # Add output edges
            for output in self.outputs:
                for input_step in output.inputs:
                    input_name = input_step.name
                    if input_name not in nodes:
                        errors.append(
                            f"Output input {input_name} not found in processing steps"
                        )
                    edges.append(Edge(source=input_step, destination=output))

        except Exception as e:
            errors.append(f"Error validating DAG: {e}")

        try:
            if detect_cycles(nodes, edges):
                errors.append("Cycle detected in the pipeline DAG")
        except ValueError as e:
            errors.append(str(e))

        if errors:
            error_message = (
                "DAG validation failed with the following errors:\n" + "\n".join(errors)
            )
            raise ValueError(error_message)
        else:
            return nodes, edges

    def _additional_validations(self):
        errors = []

        # Permissions checks
        for data_source in self.data_sources:
            if not check_permissions(
                data_source.catalog, data_source.schema, data_source.table
            ):
                errors.append(
                    f"No permissions for table {data_source.catalog}.{data_source.schema}.{data_source.table}"
                )

        if errors:
            raise Exception("Validation errors:\n" + "\n".join(errors))

    def read_data_source(self, data_source: DataSource):
        # Mock implementation of reading data from a data source
        log.info(f"Reading data from data source '{data_source.name}'")
        # Return a mock data object (e.g., a string or a simple data structure)
        return f"data_from_{data_source.name}"

    def write_output(self, table_name, result):
        log.info(f"Writing output to table '{table_name}'")
        # TODO: Implement output writing logic
        # Questions:
        # - What should write mode be?
        # - Does this handle schema changes?
        # - How do we handle errors?

        # TODO: should probably return write metadata, can get this with DESCRIBE HISTORY

    def get_step_by_name(self, step_name):
        for step in self.processing_steps:
            if step.name == step_name:
                return step
        raise ValueError(f"Step {step_name} not found in pipeline")

    def run(self) -> Run:
        """
        Run the pipeline and return the run id
        """
        run = self.metadata_manager.start_run()
        log.info("🏃 Starting run")
        console.log(run)

        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            auto_refresh=True,
            # console=console,
        ) as progress:
            # Create a task for overall pipeline progress
            pipeline_task = progress.add_task(
                description="[cyan]Running pipeline...", total=len(self.execution_order)
            )

            for node_name in self.execution_order:
                # Update description for current node
                progress.update(
                    pipeline_task,
                    refresh=True,  # required for Jupyter notebook
                )
                edges = self._get_incoming_edges(node_name)

                for edge in edges:
                    # Create a subtask for each edge execution
                    edge_task = progress.add_task(
                        f"[green]Executing {edge.source.name} → {edge.destination.name}",
                        total=100,
                        refresh=True,
                    )
                    self._execute_edge(edge, run)

                    progress.update(edge_task, completed=100)

                    # Remove the completed edge task
                    progress.remove_task(edge_task)

                progress.update(pipeline_task, advance=1)

        return run

    def _execute_edge(self, edge: Edge, run: Run):
        """Execute a single edge with progress tracking"""
        log.info(
            f"Starting edge execution: {edge.source.name} → {edge.destination.name}"
        )
        self.metadata_manager.update_step_metadata(edge.destination, run, "running")
        try:
            log.info(f"Executing edge function: {edge.function}")
            result = edge.function()
            log.info(f"Edge function completed: {result}")
        except Exception as e:
            log.error(f"Edge failed: {str(e)}")
            self.metadata_manager.update_step_metadata(edge.destination, run, "failed")
            log.info(f"Updated metadata for failed edge: {edge.destination.name}")
            raise
        self.metadata_manager.update_step_metadata(edge.destination, run, "completed")
        self.metadata_manager.write_step_result(result)

    def execute_step(self, step: ProcessingStep, run_id: str):
        # Update metadata to 'running'
        self.metadata_manager.update_step_metadata(step.name, run_id, "running")

        try:
            # get the function if it's a string
            if isinstance(step.function, str):
                module_name, function_name = step.function.rsplit(".", 1)
                module = importlib.import_module(module_name)
                step.function = getattr(module, function_name)
        except Exception:
            log.error(f"Error importing function {step.function}")
            raise

        try:
            # Resolve inputs
            input_data = []
            for input_item in step.inputs:
                if isinstance(input_item, DataSource):
                    # Read data from the data source
                    data = self.read_data_source(input_item)
                elif isinstance(input_item, ProcessingStep):
                    # Get output from previous step
                    data = self.data_store.get(input_item.name)
                    if data is None:
                        raise ValueError(
                            f"Output for step '{input_item.name}' not found."
                        )
                else:
                    raise TypeError(f"Unsupported input type: {type(input_item)}")
                input_data.append(data)

            # Execute the processing function with inputs
            result = step.function(*input_data)

            self.write_output(step.output_table, result)

            # Store the output in data_store
            self.data_store[step.name] = result

            # Update metadata to 'completed'
            self.metadata_manager.update_step_metadata(step.name, run_id, "completed")
        except Exception as e:
            # Update metadata to 'failed'
            self.metadata_manager.update_step_metadata(step.name, run_id, "failed")
            print(f"Error in step '{step.name}': {e}")
            raise

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Pipeline":
        """Create a Pipeline instance from a YAML file."""
        try:
            with open(yaml_path, "r") as f:
                config = yaml.safe_load(f)

            # Create a mapping of names to objects
            name_to_obj = {}

            # Create all data sources first
            data_sources = []
            for source_config in config.get("data_sources", []):
                source = DataSource(**source_config)
                name_to_obj[source.name] = source
                data_sources.append(source)

            # Create processing steps, resolving input references
            processing_steps = []
            for step_config in config.get("processing_steps", []):
                input_names = step_config.pop("inputs", [])
                # Resolve input references to actual objects
                input_objects = [name_to_obj[name] for name in input_names]
                step = ProcessingStep(**step_config, inputs=input_objects)
                name_to_obj[step.name] = step
                processing_steps.append(step)

            # Create outputs, resolving input references
            outputs = []
            for output_config in config.get("outputs", []):
                input_names = output_config.pop("inputs", [])
                # Resolve input references to actual objects
                input_objects = [name_to_obj[name] for name in input_names]
                output = Output(**output_config, inputs=input_objects)
                outputs.append(output)

            return cls(
                data_sources=data_sources,
                processing_steps=processing_steps,
                outputs=outputs,
            )
        except FileNotFoundError:
            raise
        except yaml.YAMLError as e:
            raise
        except KeyError as e:
            raise ValueError(f"Referenced node not found: {e}")
        except ValidationError as e:
            raise
