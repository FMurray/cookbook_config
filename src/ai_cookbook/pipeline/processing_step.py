import importlib

from pydantic import ValidationError, BaseModel, field_validator, Field
from typing import List, Union, Optional

from ai_cookbook.logging.logger import log
from ai_cookbook.pipeline.data_source import DataSource


class ProcessingStep(BaseModel):
    name: str
    function: str  # This will be a module path like "ai_cookbook.functions.parsing.parse_pdf"
    inputs: List[Union["ProcessingStep", DataSource]]
    output_table: str
    parameters: Optional[dict] = Field(default_factory=dict)

    @field_validator("function")
    def validate_function_exists(cls, v):
        try:
            # Split the function path into module path and function name
            module_path, function_name = v.rsplit(".", 1)

            # Import the module
            module = importlib.import_module(module_path)

            # Check if the function exists in the module
            if not hasattr(module, function_name):
                raise ValueError(
                    f"Function '{function_name}' not found in module '{module_path}'"
                )

            # Optionally, verify it's callable
            if not callable(getattr(module, function_name)):
                raise ValueError(
                    f"'{function_name}' in module '{module_path}' is not callable"
                )

            return v
        except ImportError:
            raise ValueError(f"Could not import module '{module_path}'")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Invalid function path: {str(e)}")

    # @field_validator("inputs")
    # @classmethod
    # def validate_inputs(cls, v, info):
    #     if not isinstance(v, (ProcessingStep, DataSource)):
    #         raise TypeError(
    #             f"Invalid input type: {type(v)}. Expected ProcessingStepConfig or DataSourceConfig."
    #         )
    #     return v


ProcessingStep.model_rebuild()
