import uuid
from datetime import datetime
from collections import defaultdict
from rich.table import Table
from rich.text import Text


class Run:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.start_time = datetime.now()

    def __rich__(self):
        table = Table(show_header=False, box=None)
        table.add_row(
            Text("Run ID: ", style="bold blue"), Text(self.run_id, style="cyan")
        )
        table.add_row(
            Text("Started: ", style="bold blue"),
            Text(str(self.start_time), style="cyan"),
        )
        return table


class MetadataManager:
    """
    In-memory metadata manager
    """

    def __init__(self):
        self.step_metadata = {}
        self.runs = {}

    def update_step_metadata(self, step, run_id, status):
        """
        Adds a new entry to the step metadata dictionary
        """
        if step.name not in self.step_metadata:
            self.step_metadata[step.name] = []
        self.step_metadata[step.name].append((run_id, status))

    def write_step_result(self, result):
        pass

    def get_metadata(self):
        return self.step_metadata

    def start_run(self):
        """
        Logs the start of a run with a unique ID and the current timestamp.
        """
        return Run(str(uuid.uuid4()))
