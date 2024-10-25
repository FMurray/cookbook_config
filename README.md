# AI Cookbook

## Overview

The AI Cookbook is a Python framework designed to simplify the creation of Generative AI (GenAI) applications, particularly focusing on Retrieval Augmented Generation (RAG). The framework enables developers to build data pipelines and AI agents using a configuration-driven approach, promoting rapid iteration and composability.

## Core Philosophy

The project is built upon three main imperatives:

1. **Configuration-Driven Development**: Define data sources, processing steps, and AI agents through configuration files or code, ensuring clarity, maintainability, and version control.

2. **Fast Time to Iterate**: Provide immediate feedback through automatic validation and state tracking, enabling developers to experiment and refine pipelines quickly without unnecessary overhead.

3. **Composability**: Utilize modular components that can be easily combined and reused, fostering flexibility and scalability in building complex GenAI applications.

## Developer Workflow

1. **Define Configurations**:
   - Use YAML/JSON files or Python code to specify data sources, processing steps, and outputs.
   - Configurations are automatically validated using Pydantic models, ensuring correctness.

2. **Implement Processing Functions**:
   - Write custom processing functions or use built-in ones to define the behavior of each processing step.
   - Functions read from input tables and write to output tables, leveraging Delta Lake for storage and versioning.

3. **Build the Pipeline**:
   - Assemble the pipeline using provided classes, linking data sources, processing steps, and outputs according to the configuration.
   - The pipeline automatically constructs a dependency graph to manage execution order.

4. **Validate and Execute**:
   - Instantiate the pipeline, triggering automatic validation.
   - Execute the pipeline to process data, with state tracking and intelligent dependency management ensuring efficient execution.

5. **Iterate Quickly**:
   - Modify configurations or processing functions as needed.
   - The system detects changes and re-executes only affected steps, facilitating rapid development cycles.

6. **Monitor and Debug**:
   - Utilize integrated logging, error handling, and MLflow tracking to monitor pipeline execution and troubleshoot issues.

## Project Structure

The project is organized into several modules, each responsible for different aspects of the pipeline framework:

```
genai_pipeline_project/
├── README.md
├── setup.py
├── requirements.txt
├── .gitignore
├── config/
│   ├── pipeline_config.yaml
│   └── logging.conf
├── data/
│   ├── raw/
│   ├── processed/
│   └── indexes/
├── notebooks/
│   ├── exploratory_analysis.ipynb
│   └── pipeline_execution.ipynb
├── scripts/
│   ├── run_pipeline.py
│   └── utils.py
├── src/
│   ├── __init__.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── pipeline.py
│   │   ├── models.py
│   │   ├── processing_step.py
│   │   ├── data_source.py
│   │   ├── vector_index.py
│   │   ├── metadata_manager.py
│   │   ├── dag.py
│   │   └── validation.py
│   ├── functions/
│   │   ├── __init__.py
│   │   ├── extract_text.py
│   │   ├── add_metadata.py
│   │   ├── clean_text.py
│   │   └── custom_functions.py
│   └── utils/
│       ├── __init__.py
│       ├── spark_utils.py
│       ├── delta_utils.py
│       ├── mlflow_utils.py
│       └── permissions_utils.py
└── tests/
    ├── __init__.py
    ├── test_pipeline.py
    ├── test_models.py
    ├── test_functions.py
    └── test_utils.py
```

### Roles and Responsibilities of Modules

#### **config/**

- **pipeline_config.yaml**: Defines data sources, processing steps, and outputs.
- **logging.conf**: Configures logging behavior, levels, and formats.

#### **data/**

- **raw/**, **processed/**, **indexes/**: Directories for data storage during development and testing.

#### **notebooks/**

- **exploratory_analysis.ipynb**: For data exploration and function prototyping.
- **pipeline_execution.ipynb**: For interactive pipeline execution and debugging.

#### **scripts/**

- **run_pipeline.py**: Command-line script to execute the pipeline.
- **utils.py**: Helper functions for scripts.

#### **src/**

##### **pipeline/**

- **models.py**: Contains Pydantic models for configuration schemas, ensuring automatic validation upon instantiation.
- **pipeline.py**: Implements the `Pipeline` class, orchestrating pipeline execution.
- **processing_step.py**: Defines the `ProcessingStep` class, representing individual steps in the pipeline.
- **data_source.py**: Defines the `DataSource` class, representing data inputs.
- **vector_index.py**: Defines the `VectorIndex` class for creating vector indexes.
- **metadata_manager.py**: Manages metadata for state tracking and execution status.
- **dag.py**: Handles dependency graph construction and execution ordering.
- **validation.py**: Contains additional validation logic not covered by Pydantic models (optional).

##### **functions/**

- **extract_text.py**, **add_metadata.py**, **clean_text.py**, **custom_functions.py**:
  - Contain processing functions that perform specific data transformations.
  - Functions read from input tables and write to output tables.

##### **utils/**

- **spark_utils.py**: Manages Spark session initialization and configurations.
- **delta_utils.py**: Provides functions for interacting with Delta Lake tables.
- **mlflow_utils.py**: Integrates MLflow for experiment tracking and logging.
- **permissions_utils.py**: Checks user permissions and validates naming conventions.

#### **tests/**

- **test_pipeline.py**: Tests for the `Pipeline` class and execution logic.
- **test_models.py**: Tests for Pydantic models to ensure configurations are validated correctly.
- **test_functions.py**: Tests for processing functions.
- **test_utils.py**: Tests for utility functions.

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/genai_pipeline_project.git
   cd genai_pipeline_project
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install --upgrade pip
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Pipeline**:
   - Edit `config/pipeline_config.yaml` to define your data sources, processing steps, and outputs.

5. **Implement Processing Functions**:
   - Add custom processing logic in `src/functions/` or use existing functions.

6. **Run the Pipeline**:
   ```bash
   python scripts/run_pipeline.py --config config/pipeline_config.yaml
   ```

7. **Monitor Execution**:
   - Check logs and MLflow UI for execution details and performance metrics.

## Core Components

### **Pipeline Execution (`pipeline.py`)**

- **Initialization**:
  - Loads and validates configurations using Pydantic models.
  - Builds the dependency graph based on processing steps.

- **Execution**:
  - Processes data sources and executes processing steps in order.
  - Manages state tracking, caching intermediate results, and handling dependencies.

- **State Tracking**:
  - Uses Delta Lake's versioning and metadata to track data lineage.
  - Stores execution metadata for auditing and reproducibility.

### **Processing Functions (`functions/`)**

- Define the behavior of processing steps.
- Should read from input tables and write to output tables.
- Follow a consistent interface for compatibility with the pipeline.

### **Utilities (`utils/`)**

- **Spark Utilities**:
  - Initialize and manage Spark sessions.
  - Configure Spark settings for optimal performance.

- **Delta Lake Utilities**:
  - Read from and write to Delta Lake tables.
  - Retrieve table versions and schemas.

- **MLflow Utilities**:
  - Log configurations, parameters, and artifacts.
  - Facilitate experiment tracking and comparison.

- **Permissions Utilities**:
  - Validate user permissions for data operations.
  - Ensure compliance with naming conventions.

## Best Practices

- **Configuration-Driven**:
  - Keep all pipeline definitions in configuration files for consistency and version control.

- **Modular Design**:
  - Write reusable processing functions and components.
  - Utilize the composability of the framework to build complex pipelines from simple parts.

- **Validation and Error Handling**:
  - Leverage automatic validation with Pydantic models.
  - Implement comprehensive error handling and provide clear error messages.

- **Logging and Monitoring**:
  - Use the provided logging configurations to monitor pipeline execution.
  - Track experiments and data lineage with MLflow and Delta Lake.

- **Testing**:
  - Write unit tests for processing functions and pipeline components.
  - Ensure that changes do not break existing functionality.

## Contributing

Contributions are welcome! Please follow these guidelines:

- **Fork the Repository**: Create a personal fork of the project.

- **Create a Feature Branch**:
  ```bash
  git checkout -b feature/your-feature-name
  ```

- **Implement Your Feature**: Make changes in a modular and testable manner.

- **Write Tests**: Ensure your code is covered by unit tests.

- **Submit a Pull Request**: Provide a clear description of your changes and the problem they solve.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue in the GitHub repository or contact the maintainers directly.

---

By adhering to the core philosophy and utilizing the modular structure of this framework, developers can efficiently build and manage GenAI applications with ease and confidence.