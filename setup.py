from setuptools import setup, find_packages

setup(
    name="ai_cookbook",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "ai_cookbook": [
            "*.conf",
            "*.yaml",
        ],  # Include all .conf and .yaml files in config
    },
    # Or use MANIFEST.in instead of package_data
    include_package_data=True,
    install_requires=[
        "databricks-sdk",
        "mlflow",
        "pydantic-settings",
        "pydantic",
        "pyyaml",
        "requests",
        "rich",
    ],
)
