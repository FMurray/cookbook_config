from typing import List
from pydantic import ValidationError, BaseModel

from src.pipeline.data_source import DataSource
from src.pipeline.processing_step import ProcessingStep
from src.pipeline.output import Output
from src.logging.logger import log

from .validation import check_permissions
from .dag import topological_sort, detect_cycles


class Pipeline(BaseModel):
    data_sources: List[DataSource]
    processing_steps: List[ProcessingStep]
    outputs: List[Output]
    execution_order: List[str] = []  # Add this line to declare the field

    def model_post_init(self, __context):
        try:
            self._validate_dag()
        except ValueError as e:
            log.error(e)
            raise

    def _build_dag(self):
        dag = {}
        for step in self.processing_steps:
            dag[step.name] = {"step": step, "depends_on": step.inputs}
        return dag

    def _validate_dag(self):
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
                    nodes[ds.name] = ds.name

            # Add processing steps to nodes
            for step in self.processing_steps:
                if step.name in nodes:
                    errors.append(f"Duplicate processing step name: {step.name}")
                else:
                    nodes[step.name] = step

            # Add output nodes
            for output in self.outputs:
                nodes[f"output_{output.name}"] = output.name

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
                        edges.append((input_name, step.name))

            # Add output edges
            for output in self.outputs:
                for input_step in output.inputs:
                    input_name = input_step.name
                    if input_name not in nodes:
                        errors.append(
                            f"Output input {input_name} not found in processing steps"
                        )
                    edges.append((input_name, f"output_{output.name}"))

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
            self.execution_order = topological_sort(nodes, edges)

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

    def run(self):
        if False:
            # Execute data sources and processing steps
            for ds in self.data_sources:
                self._ingest_data_source(ds)
            for step in self.processing_steps:
                self._execute_processing_step(step)
            for output in self.outputs:
                self._create_vector_index(output)
            # Log to MLflow
            self._log_to_mlflow()
        log.info("✅ YAY IT RAN")
