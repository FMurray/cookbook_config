from setuptools import setup, find_packages

setup(
    name="genai_cookbook",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "databricks-sdk",
        "mlflow",
        "pydantic-settings",
        "pydantic",
        "pyyaml",
        "requests",
    ],
)
