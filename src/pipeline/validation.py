from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)


def validate_pipeline_config(config):
    errors = []
    # Validate data sources
    errors.extend(validate_data_sources(config.get("data_sources", [])))
    # Validate processing steps
    errors.extend(validate_processing_steps(config.get("processing_steps", [])))
    # Validate outputs
    errors.extend(validate_outputs(config.get("outputs", [])))

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors)


def validate_data_sources(data_sources):
    errors = []
    for ds in data_sources:
        # Check required fields
        required_fields = [
            "name",
            "type",
            "path",
            "format",
            "catalog",
            "schema",
            "table",
        ]
        missing_fields = [field for field in required_fields if field not in ds]
        if missing_fields:
            errors.append(
                f"Data source '{ds.get('name', 'unknown')}' is missing fields: {missing_fields}"
            )
        # Additional validations can be added here
    return errors


def validate_processing_steps(steps):
    errors = []
    for step in steps:
        # Check required fields
        required_fields = ["name", "function", "inputs", "output_table"]
        missing_fields = [field for field in required_fields if field not in step]
        if missing_fields:
            errors.append(
                f"Processing step '{step.get('name', 'unknown')}' is missing fields: {missing_fields}"
            )
        # Validate function existence
        if "function" in step:
            function_name = step["function"]
            # Assume functions are available in src.functions
            from src.functions import __dict__ as functions_dict

            if function_name not in functions_dict:
                errors.append(
                    f"Function '{function_name}' for step '{step['name']}' does not exist."
                )
        # Additional validations can be added here
    return errors


def validate_outputs(outputs):
    errors = []
    for output in outputs:
        # Check required fields
        required_fields = ["name", "type", "inputs", "embedding_model", "output_table"]
        missing_fields = [field for field in required_fields if field not in output]
        if missing_fields:
            errors.append(
                f"Output '{output.get('name', 'unknown')}' is missing fields: {missing_fields}"
            )
        # Additional validations can be added here
    return errors


def check_permissions(catalog, schema, table):
    return True
