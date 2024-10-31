from pydantic import BaseModel
from typing import Optional, TypeVar, Generic

T = TypeVar("T")
E = TypeVar("E")


class Result(BaseModel, Generic[T, E]):
    data: Optional[T] = None
    error: Optional[E] = None
    source_table: Optional[str] = None
    source_volume: Optional[str] = None
    destination_table: str
    success_rows: int
    error_rows: int

    def is_ok(self) -> bool:
        """Check if the result is successful."""
        return self.error is None

    def is_err(self) -> bool:
        """Check if the result contains an error."""
        return self.error is not None

    def unwrap(self) -> T:
        """Get the success value or raise an exception if there's an error."""
        if self.error is not None:
            raise ValueError(f"Called unwrap on an error result: {self.error}")
        return self.data

    def unwrap_or(self, default: T) -> T:
        """Get the success value or return the default if there's an error."""
        return self.data if self.is_ok() else default

    def unwrap_err(self) -> E:
        """Get the error value or raise an exception if there's no error."""
        if self.error is None:
            raise ValueError("Called unwrap_err on an OK result")
        return self.error
