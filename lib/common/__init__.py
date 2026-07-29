import subprocess

from enum import Enum

class ProcTerminateType(Enum):
    SUCCESS = 0
    TLE = 1
    RE = 2
    ERROR = 3

class ProcRunResult:
    def __init__(self, type, output, returncode, err):
        self.type = type
        self.output = output
        self.returncode = returncode
        self.error = err

    def get_message(self):
        if self.type == ProcTerminateType.SUCCESS: return "Success"
        if self.type == ProcTerminateType.TLE: return "Time Limit Exceeded"
        if self.type == ProcTerminateType.RE: return "Runtime Error (Return code %d)" % self.returncode
        if self.type == ProcTerminateType.ERROR: return "Error"
        return ""
    
def run_process(executable, inputs, max_runtime = 1.0):
    """ Runs the targeted executable file with the given input. Returns a ProcRunResult instance. """
    try:
        proc = subprocess.Popen(executable, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.DEVNULL, bufsize = 1, text = True)
        output, _ = proc.communicate(input = inputs, timeout = 1e9 if max_runtime < 0 else max_runtime)
        return ProcRunResult(ProcTerminateType.SUCCESS, output, 0, None)
    except subprocess.CalledProcessError as err:
        return ProcRunResult(ProcTerminateType.RE, "", str(err.returncode), 0, err)
    except subprocess.TimeoutExpired as err:
        return ProcRunResult(ProcTerminateType.TLE, "", None, err)
    except Exception as err:
        return ProcRunResult(ProcTerminateType.ERROR, "", None, err)