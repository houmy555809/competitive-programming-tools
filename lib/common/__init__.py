import subprocess
from enum import Enum


class ProcTerminateType(Enum):
    SUCCESS = 0
    TLE = 1
    RE = 2
    ERROR = 3


class ProcRunResult:
    def __init__(self, terminate_type, output, returncode, err):
        self.terminate_type = terminate_type
        self.output = output
        self.returncode = returncode
        self.error = err

    def get_message(self):
        if self.terminate_type == ProcTerminateType.SUCCESS:
            return "Success"
        if self.terminate_type == ProcTerminateType.TLE:
            return "Time Limit Exceeded"
        if self.terminate_type == ProcTerminateType.RE:
            return f"Runtime Error (Return code {self.returncode})"
        if self.terminate_type == ProcTerminateType.ERROR:
            return "Error"
        return ""


def run_process(executable, inputs, max_runtime = 1.0):
    """Runs the targeted executable file with the given input. Returns a ProcRunResult instance."""
    try:
        proc = subprocess.Popen(executable, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.DEVNULL, bufsize = 1, text = True)
        output, _ = proc.communicate(input = inputs, timeout = 1e9 if max_runtime < 0 else max_runtime)
        if proc.returncode == 0:
            return ProcRunResult(ProcTerminateType.SUCCESS, output, 0, None)
        return ProcRunResult(ProcTerminateType.RE, output, proc.returncode, None)
    except subprocess.TimeoutExpired as err:
        return ProcRunResult(ProcTerminateType.TLE, "", None, err)
    except Exception as err:
        return ProcRunResult(ProcTerminateType.ERROR, "", None, err)
