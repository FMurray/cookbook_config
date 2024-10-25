from pydantic import ValidationError

from .models import PipelineConfig
from .validation import check_permissions


class Pipeline:
    def __init__(self, config_data):
        try:
            self.config = PipelineConfig(**config_data)
        except ValidationError as e:
            print("Configuration validation failed:")
            print(e)
            raise

    def _build_dag(self):
        dag = {}
        for step in self.processing_steps:
            dag[step.name] = {"step": step, "depends_on": step.inputs}
        return dag

    def _additional_validations(self):
        errors = []

        # Permissions checks
        for data_source in self.config.data_sources:
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
