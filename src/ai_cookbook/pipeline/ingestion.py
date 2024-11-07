from pydantic import BaseModel

from ai_cookbook.logging.logger import log
from ai_cookbook.pipeline.result import Result
from ai_cookbook.pipeline.data_source import DataSource
from ai_cookbook.pipeline.processing_step import ProcessingStep

from typing import TypeAlias


class IngestionError(BaseModel):
    message: str
    code: int


class IngestionData(BaseModel):
    processed_records: int
    timestamp: str


IngestionResult: TypeAlias = Result[IngestionData, IngestionError]


def ingest_volume(source: DataSource, destination: ProcessingStep):
    try:
        records_processed = 100

        destination.function()

        return True

        # TODO: this is funky, I'll fix it later

        return IngestionResult(
            data=IngestionData(processed_records=records_processed),
            source_volume=source.volume_name,
            destination_table=destination.output_table,
            success_rows=records_processed,
            error_rows=0,
        )
    except Exception as e:
        error_rows = 1

        return IngestionResult(
            error=IngestionError(message=str(e), code=500),
            source_volume=source,
            destination_table=destination,
            success_rows=0,
            error_rows=error_rows,
        )


def ingest_data(source: str, destination: str) -> IngestionResult:
    """
    Ingest data from source to destination table.
    Returns IngestionResult with either success data or error information.
    """
    try:
        records_processed = 100

        return IngestionResult(
            data=IngestionData(processed_records=records_processed),
            source_table=source,
            destination_table=destination,
            success_rows=records_processed,
            error_rows=0,
        )
    except Exception as e:
        return IngestionResult(
            error=IngestionError(message=str(e), code=500),
            source_table=source,
            destination_table=destination,
            success_rows=0,
            error_rows=1,
        )
