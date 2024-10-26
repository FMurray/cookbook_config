import os
import pkg_resources


# Get paths to config files
def get_config_path(filename):
    try:
        return pkg_resources.resource_filename("ai_cookbook", os.path.join(filename))
    except Exception as e:
        # Fallback for development
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        return os.path.join(project_root, "config", filename)


# Common config paths
LOGGING_CONFIG = get_config_path("logging.conf")
PIPELINE_CONFIG = get_config_path("pipeline_config.yaml")
