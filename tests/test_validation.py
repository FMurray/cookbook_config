# tests/test_validation.py

import unittest
from src.pipeline.validation import validate_pipeline_config, ValidationResult


class TestValidation(unittest.TestCase):
    def test_valid_config(self):
        config = {
            "data_sources": [
                {
                    "name": "financial_reports",
                    "type": "volume",
                    "path": "s3://bucket/path/to/pdfs/",
                    "format": "pdf",
                    "catalog": "main_catalog",
                    "schema": "raw_data",
                    "table": "financial_reports",
                }
            ],
            "processing_steps": [
                {
                    "name": "extract_text",
                    "function": "extract_text_from_pdf",
                    "inputs": ["main_catalog.raw_data.financial_reports"],
                    "output_table": "main_catalog.processed_data.extracted_texts",
                }
            ],
            "outputs": [
                {
                    "name": "financial_reports_index",
                    "type": "vector_index",
                    "inputs": ["main_catalog.processed_data.extracted_texts"],
                    "embedding_model": "openai-embedding-model",
                    "output_table": "main_catalog.indexes.financial_reports_index",
                }
            ],
        }
        result = validate_pipeline_config(config)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_invalid_config_missing_fields(self):
        config = {
            "data_sources": [
                {
                    "name": "financial_reports",
                    "type": "volume",
                    # Missing 'path', 'format', 'catalog', 'schema', 'table'
                }
            ]
        }
        result = validate_pipeline_config(config)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertIn(
            "Data source 'financial_reports' is missing fields", result.errors[0]
        )


if __name__ == "__main__":
    unittest.main()
