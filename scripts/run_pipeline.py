from ai_cookbook.logging.logger import log, handle_exception
import sys

import argparse
from ai_cookbook.pipeline.pipeline import Pipeline
import yaml


def main(config_path):
    # Load configuration
    # with open(config_path, "r") as f:
    #     config_data = yaml.safe_load(f)

    # Initialize the pipeline
    try:
        pipeline = Pipeline.from_yaml(config_path)
    except Exception as e:
        log.exception("💔 Pipeline initialization failed:")
        return  # Exit or raise an exception

    log.info("🔨 Pipeline initialized successfully. Executing pipeline...")
    pipeline.run()


if __name__ == "__main__":
    log.info("🍃 Starting pipeline execution...")
    parser = argparse.ArgumentParser(description="Run the GenAI data pipeline.")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the pipeline configuration file.",
    )
    args = parser.parse_args()

    sys.excepthook = handle_exception

    try:
        main(args.config)
    except Exception as e:
        log.error(e)
        # raise
