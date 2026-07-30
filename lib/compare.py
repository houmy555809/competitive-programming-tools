from enum import Enum
from colorama import *
import tempfile
import os
import ast

from . import common, cache, workspace

class ValidationStatus(Enum):
    GENERATING_DATA = 0
    RUNNING_PROGA = 1
    RUNNING_PROGB = 2
    JUDGING = 3
    PASSED = 4
    WRONG = 5
    FAILED = 6

class ValidationResultType(Enum):
    PASSED = 0
    WRONG = 1
    DATAGEN_FAILED = 2
    PROGA_RUN_FAILED = 3
    PROGB_RUN_FAILED = 4
    JUDGE_FAILED = 5
    ERROR = 6

class ValidationResult:
    def __init__(self, type, datagen_result, progA_result, progB_result, judger_result, msg, err):
        self.type = type
        self.datagen_result = datagen_result
        self.progA_result = progA_result
        self.progB_result = progB_result
        self.judger_result = judger_result
        self.msg = msg
        self.err = err

_last_msg = ""
tot_steps = 0
passed_steps = 0

def _set_status(prefix, status, msg):
    global _last_msg

    color = Style.RESET_ALL
    newline = False
    if status == ValidationStatus.GENERATING_DATA: color, newline = Fore.LIGHTBLACK_EX, False
    if status == ValidationStatus.RUNNING_PROGA: color, newline = Fore.LIGHTBLACK_EX, False
    if status == ValidationStatus.RUNNING_PROGB: color, newline = Fore.LIGHTBLACK_EX, False
    if status == ValidationStatus.JUDGING: color, newline = Fore.LIGHTBLACK_EX, False
    if status == ValidationStatus.PASSED: color, newline = Fore.LIGHTGREEN_EX, True
    if status == ValidationStatus.WRONG: color, newline = Fore.RED, True
    if status == ValidationStatus.FAILED: color, newline = Fore.RED, True

    padding = " " * max(len(_last_msg) - len(prefix + ' ' + msg), 0)
    print('\r' + color + prefix + ' ' + msg + Style.RESET_ALL, end = padding)
    print('\r' + color + prefix + ' ' + msg + Style.RESET_ALL, end = ("\n" if newline else ""))
    _last_msg = prefix + ' ' + msg


def _validate_once(prefix, datagen, progA, progB, judger, max_runtime, caching):
    """ Runs the whole process once. Returns a ValidationResult instance. """

    if isinstance(max_runtime, float):
        max_runtime = (max_runtime, max_runtime, max_runtime, max_runtime)

    try:
        _set_status(prefix, ValidationStatus.GENERATING_DATA, "Generating Data ...")
        datagen_result = common.run_process(datagen, "", max_runtime[0])
        if datagen_result.type != common.ProcTerminateType.SUCCESS:
            _set_status(prefix, ValidationStatus.FAILED, "Data Generation Failed")
            return ValidationResult(ValidationResultType.DATAGEN_FAILED, datagen_result, None, None, None, "Data generation failed", None)
        generated_data = datagen_result.output
        fd_data, path_data = tempfile.mkstemp()
        open(fd_data, "w").write(generated_data)

        _set_status(prefix, ValidationStatus.RUNNING_PROGA, "Running Program A ...")
        progA_result = common.run_process(progA, generated_data, max_runtime[1])
        if progA_result.type != common.ProcTerminateType.SUCCESS:
            message = "Program A " + progA_result.get_message()
            _set_status(prefix, ValidationStatus.FAILED, message)
            if caching in ("all", "failures", "both"):
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", "")
                cache.dump_file(prefix, "progB.out", "")
                cache.dump_file(prefix, "message.txt", message)
            return ValidationResult(ValidationResultType.PROGA_RUN_FAILED, datagen_result, progA_result, None, None, message, None)
        progA_output = progA_result.output
        fd_progA, path_progA = tempfile.mkstemp()
        open(fd_progA, "w").write(progA_output)

        _set_status(prefix, ValidationStatus.RUNNING_PROGB, "Running Program B ...")
        progB_result = common.run_process(progB, generated_data, max_runtime[2])
        if progB_result.type != common.ProcTerminateType.SUCCESS:
            message = "Program B " + progB_result.get_message()
            _set_status(prefix, ValidationStatus.FAILED, message)
            if caching in ("all", "failures", "both"):
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", progA_output)
                cache.dump_file(prefix, "progB.out", "")
                cache.dump_file(prefix, "message.txt", message)
            return ValidationResult(ValidationResultType.PROGB_RUN_FAILED, datagen_result, progA_result, progB_result, None, message, None)
        progB_output = progB_result.output
        fd_progB, path_progB = tempfile.mkstemp()
        open(fd_progB, "w").write(progB_output)

        _set_status(prefix, ValidationStatus.JUDGING, "Judging ...")
        judger_result = common.run_process(judger + [path_data, path_progA, path_progB], "", max_runtime[3])
        if judger_result.type != common.ProcTerminateType.SUCCESS:
            _set_status(prefix, ValidationStatus.FAILED, "Judgement Failed")
            if caching in ("all", "failures", "both"):
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", progA_output)
                cache.dump_file(prefix, "progB.out", progB_output)
                cache.dump_file(prefix, "message.txt", "Judgement Failed")
            return ValidationResult(ValidationResultType.JUDGE_FAILED, datagen_result, progA_result, progB_result, judger_result, "Judgement Failed", None)
        judger_output = judger_result.output.strip()

        is_accepted = judger_output.startswith("OK") or judger_output.startswith("AC")

        if is_accepted:
            _set_status(prefix, ValidationStatus.PASSED, "Accepted")
            if caching == "all":
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", progA_output)
                cache.dump_file(prefix, "progB.out", progB_output)
                cache.dump_file(prefix, "judger.txt", judger_output)
            return ValidationResult(ValidationResultType.PASSED, datagen_result, progA_result, progB_result, judger_result, "Accepted", None)
        else:
            _set_status(prefix, ValidationStatus.WRONG, "Wrong Answer")
            if caching in ("all", "mismatches", "both"):
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", progA_output)
                cache.dump_file(prefix, "progB.out", progB_output)
                cache.dump_file(prefix, "judger.txt", judger_output)
            return ValidationResult(ValidationResultType.WRONG, datagen_result, progA_result, progB_result, judger_result, "Wrong Answer", None)
    except Exception as err:
        _set_status(prefix, ValidationStatus.FAILED, "Error while validating: " + str(err))
        return ValidationResult(ValidationResultType.ERROR, None, None, None, None, "Error while validating: " + str(err), err)

def _show_summary():
    global tot_steps, passed_steps
    print()
    print("Stopped.")
    print("# of cases tested: ", tot_steps)
    print("# of cases passed: ", passed_steps)
    print()

def _handle_mismatch(mismatch_strategy):
    if mismatch_strategy == "continue": pass
    elif mismatch_strategy == "stop":
        _show_summary()
        exit(0)
    elif mismatch_strategy == "pause":
        inp = input(Fore.LIGHTBLUE_EX + "Continue (y/n)?" + Style.RESET_ALL)
        while inp not in "ynYN":
            inp = input(Fore.LIGHTBLUE_EX + "Continue (y/n)?" + Style.RESET_ALL)
        if inp in "nN":
            _show_summary()
            exit(0)

def work(args):
    global tot_steps, passed_steps

    datagen = [args.datagen]
    program_a = [args.program_a]
    program_b = [args.program_b]
    judger = [args.judger]

    use_workspace = args.use_workspace
    if use_workspace:
        cur_workspace = workspace.get_workspace()
        if cur_workspace is None:
            print("No workspace assigned. Please disable the -w/--workspace argument or assign a workspace with `cpt workspace`.")
            exit(0)
        datagen[0] = os.path.join(cur_workspace.path, datagen[0])
        program_a[0] = os.path.join(cur_workspace.path, program_a[0])
        program_b[0] = os.path.join(cur_workspace.path, program_b[0])
        judger[0] = os.path.join(cur_workspace.path, judger[0])

    strategy = args.strategy
    mismatch_strategy = args.mismatch
    n_steps = args.num_steps
    max_runtime = args.max_runtime
    caching = args.caching

    max_runtime = ast.literal_eval(args.max_runtime)

    try:
        if strategy == "limited_steps":
            for step_id in range(1, n_steps + 1):
                tot_steps += 1
                res = _validate_once(str(step_id), datagen, program_a, program_b, judger, max_runtime, caching)
                if res.type != ValidationResultType.PASSED:
                    _handle_mismatch(mismatch_strategy)
                else: passed_steps += 1
            _show_summary()
            exit(0)
        elif strategy == "nonstop":
            while True:
                tot_steps += 1
                res = _validate_once(str(tot_steps), datagen, program_a, program_b, judger, max_runtime, caching)
                if res.type != ValidationResultType.PASSED:
                    _handle_mismatch(mismatch_strategy)
                else: passed_steps += 1
    except KeyboardInterrupt:
        _show_summary()
        exit(0)