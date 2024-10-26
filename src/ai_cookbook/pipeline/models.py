# from pydantic import BaseModel, field_validator, Field
# from typing import List, Optional, Union
# import re
# import importlib

# from ai_cookbook.pipeline.data_source import DataSource
# from ai_cookbook.pipeline.processing_step import ProcessingStep
# from ai_cookbook.pipeline.output import Output


# class PipelineConfig(BaseModel):
#     @field_validator("outputs")
#     def validate_outputs(cls, v):
#         # TODO: we may not need to define an outputs
#         if len(v) == 0:
#             raise ValueError("Need to define at least one output")
#         return v

#     def __init__(self, **data):
#         # Convert DataSource objects to dictionaries
#         if "data_sources" in data:
#             data_sources = []
#             for ds in data["data_sources"]:
#                 if hasattr(ds, "config"):
#                     ds_dict = ds.config.model_dump()
#                 else:
#                     ds_dict = ds
#                 data_sources.append(ds_dict)
#             data["data_sources"] = data_sources

#         # Convert ProcessingStep objects to dictionaries
#         if "processing_steps" in data:
#             processing_steps = []
#             for step in data["processing_steps"]:
#                 if hasattr(step, "config"):
#                     step_dict = step.config.model_dump()
#                 else:
#                     step_dict = step
#                 step_dict["__pipeline_config__"] = self
#                 processing_steps.append(step_dict)
#             data["processing_steps"] = processing_steps

#         # Convert Output objects to dictionaries
#         if "outputs" in data:
#             outputs = []
#             for output in data["outputs"]:
#                 if hasattr(output, "config"):
#                     output_dict = output.config.model_dump()
#                 else:
#                     output_dict = output
#                 outputs.append(output_dict)
#             data["outputs"] = outputs

#         super().__init__(**data)


# # to support recursive validation
# ProcessingStepConfig.model_rebuild()
