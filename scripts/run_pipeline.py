import argparse
from src.pipeline.pipeline import Pipeline
import yaml


def main(config_path):
    # Load configuration
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    # Initialize the pipeline
    try:
        pipeline = Pipeline(config_data)
    except Exception as e:
        print("Pipeline initialization failed:")
        print(e)
        return  # Exit or raise an exception

    print("Pipeline initialized successfully. Executing pipeline...")
    pipeline.execute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the GenAI data pipeline.")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the pipeline configuration file.",
    )
    args = parser.parse_args()

    main(args.config)
