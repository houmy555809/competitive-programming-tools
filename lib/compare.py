import ast
import os
import tempfile
from enum import Enum

from colorama import Fore, Style

from . import cache, common, workspace


class ValidationStatus(Enum):
    GENERATING_DATA = 0
    RUNNING_PROGRAM_A = 1
    RUNNING_PROGRAM_B = 2
    JUDGING = 3
    PASSED = 4
    WRONG = 5
    FAILED = 6


class ValidationResultType(Enum):
    PASSED = 0
    WRONG = 1
    DATAGEN_FAILED = 2
    PROGRAM_A_RUN_FAILED = 3
    PROGRAM_B_RUN_FAILED = 4
    JUDGE_FAILED = 5
    ERROR = 6


class ValidationResult:
    def __init__(self, result_type, datagen_result, program_a_result, program_b_result, judger_result, msg, err):
        self.result_type = result_type
        self.datagen_result = datagen_result
        self.program_a_result = program_a_result
        self.program_b_result = program_b_result
        self.judger_result = judger_result
        self.msg = msg
        self.err = err


_last_msg = ""
tot_steps = 0
passed_steps = 0

_STATUS_STYLES = {
    ValidationStatus.GENERATING_DATA: (Fore.LIGHTBLACK_EX, False),
    ValidationStatus.RUNNING_PROGRAM_A: (Fore.LIGHTBLACK_EX, False),
    ValidationStatus.RUNNING_PROGRAM_B: (Fore.LIGHTBLACK_EX, False),
    ValidationStatus.JUDGING: (Fore.LIGHTBLACK_EX, False),
    ValidationStatus.PASSED: (Fore.LIGHTGREEN_EX, True),
    ValidationStatus.WRONG: (Fore.RED, True),
    ValidationStatus.FAILED: (Fore.RED, True),
}


def _set_status(prefix, status, msg):
    global _last_msg

    color, newline = _STATUS_STYLES[status]
    line = prefix + " " + msg
    padding = " " * max(len(_last_msg) - len(line), 0)
    print("\r" + color + line + Style.RESET_ALL, end = padding + ("\n" if newline else ""))
    _last_msg = line


def _validate_once(prefix, datagen, program_a, program_b, judger, max_runtime, caching):
    """Runs the whole process once. Returns a ValidationResult instance."""

    if isinstance(max_runtime, float):
        max_runtime = (max_runtime, max_runtime, max_runtime, max_runtime)

    temp_paths = []
    try:
        _set_status(prefix, ValidationStatus.GENERATING_DATA, "Generating Data ...")
        datagen_result = common.run_process(datagen, "", max_runtime[0])
        if datagen_result.terminate_type != common.ProcTerminateType.SUCCESS:
            _set_status(prefix, ValidationStatus.FAILED, "Data Generation Failed")
            return ValidationResult(ValidationResultType.DATAGEN_FAILED, datagen_result, None, None, None, "Data generation failed", None)
        generated_data = datagen_result.output
        with tempfile.NamedTemporaryFile("w", delete = False) as f:
            f.write(generated_data)
            path_data = f.name
        temp_paths.append(path_data)

        _set_status(prefix, ValidationStatus.RUNNING_PROGRAM_A, "Running Program A ...")
        program_a_result = common.run_process(program_a, generated_data, max_runtime[1])
        if program_a_result.terminate_type != common.ProcTerminateType.SUCCESS:
            message = "Program A " + program_a_result.get_message()
            _set_status(prefix, ValidationStatus.FAILED, message)
            if caching in ("all", "failures", "both"):
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", "")
                cache.dump_file(prefix, "progB.out", "")
                cache.dump_file(prefix, "message.txt", message)
            return ValidationResult(ValidationResultType.PROGRAM_A_RUN_FAILED, datagen_result, program_a_result, None, None, message, None)
        program_a_output = program_a_result.output
        with tempfile.NamedTemporaryFile("w", delete = False) as f:
            f.write(program_a_output)
            path_program_a = f.name
        temp_paths.append(path_program_a)

        _set_status(prefix, ValidationStatus.RUNNING_PROGRAM_B, "Running Program B ...")
        program_b_result = common.run_process(program_b, generated_data, max_runtime[2])
        if program_b_result.terminate_type != common.ProcTerminateType.SUCCESS:
            message = "Program B " + program_b_result.get_message()
            _set_status(prefix, ValidationStatus.FAILED, message)
            if caching in ("all", "failures", "both"):
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", program_a_output)
                cache.dump_file(prefix, "progB.out", "")
                cache.dump_file(prefix, "message.txt", message)
            return ValidationResult(ValidationResultType.PROGRAM_B_RUN_FAILED, datagen_result, program_a_result, program_b_result, None, message, None)
        program_b_output = program_b_result.output
        with tempfile.NamedTemporaryFile("w", delete = False) as f:
            f.write(program_b_output)
            path_program_b = f.name
        temp_paths.append(path_program_b)

        _set_status(prefix, ValidationStatus.JUDGING, "Judging ...")
        judger_result = common.run_process(judger + [path_data, path_program_a, path_program_b], "", max_runtime[3])
        if judger_result.terminate_type != common.ProcTerminateType.SUCCESS:
            _set_status(prefix, ValidationStatus.FAILED, "Judger Failed")
            if caching in ("all", "failures", "both"):
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", program_a_output)
                cache.dump_file(prefix, "progB.out", program_b_output)
                cache.dump_file(prefix, "message.txt", "Judger Failed")
            return ValidationResult(ValidationResultType.JUDGE_FAILED, datagen_result, program_a_result, program_b_result, judger_result, "Judger Failed", None)
        judger_output = judger_result.output.strip()

        is_accepted = judger_output.startswith("OK") or judger_output.startswith("AC")

        if is_accepted:
            _set_status(prefix, ValidationStatus.PASSED, "Accepted")
            if caching == "all":
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", program_a_output)
                cache.dump_file(prefix, "progB.out", program_b_output)
                cache.dump_file(prefix, "judger.txt", judger_output)
            return ValidationResult(ValidationResultType.PASSED, datagen_result, program_a_result, program_b_result, judger_result, "Accepted", None)
        else:
            _set_status(prefix, ValidationStatus.WRONG, "Wrong Answer")
            if caching in ("all", "mismatches", "both"):
                cache.dump_file(prefix, "data.in", generated_data)
                cache.dump_file(prefix, "progA.out", program_a_output)
                cache.dump_file(prefix, "progB.out", program_b_output)
                cache.dump_file(prefix, "judger.txt", judger_output)
            return ValidationResult(ValidationResultType.WRONG, datagen_result, program_a_result, program_b_result, judger_result, "Wrong Answer", None)
    except Exception as err:
        _set_status(prefix, ValidationStatus.FAILED, "Error while validating: " + str(err))
        return ValidationResult(ValidationResultType.ERROR, None, None, None, None, "Error while validating: " + str(err), err)
    finally:
        for path in temp_paths:
            try:
                os.unlink(path)
            except OSError:
                pass


def _show_summary():
    print()
    print("Stopped.")
    print(f"# of cases tested: {tot_steps}")
    print(f"# of cases passed: {passed_steps}")
    print()


def _handle_mismatch(mismatch_strategy):
    if mismatch_strategy == "continue":
        pass
    elif mismatch_strategy == "stop":
        _show_summary()
        exit(0)
    elif mismatch_strategy == "pause":
        prompt = Fore.LIGHTBLUE_EX + "Continue (y/n)?" + Style.RESET_ALL
        inp = input(prompt)
        while inp.lower() not in ("y", "n"):
            inp = input(prompt)
        if inp.lower() == "n":
            _show_summary()
            exit(0)


def work(args):
    global tot_steps, passed_steps

    datagen = [args.datagen]
    program_a = [args.program_a]
    program_b = [args.program_b]
    judger = [args.judger]

    if args.use_workspace:
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
    caching = args.caching
    max_runtime = ast.literal_eval(args.max_runtime)

    try:
        if strategy == "limited_steps":
            for step_id in range(1, n_steps + 1):
                tot_steps += 1
                res = _validate_once(str(step_id), datagen, program_a, program_b, judger, max_runtime, caching)
                if res.result_type != ValidationResultType.PASSED:
                    _handle_mismatch(mismatch_strategy)
                else:
                    passed_steps += 1
            _show_summary()
            exit(0)
        elif strategy == "nonstop":
            while True:
                tot_steps += 1
                res = _validate_once(str(tot_steps), datagen, program_a, program_b, judger, max_runtime, caching)
                if res.result_type != ValidationResultType.PASSED:
                    _handle_mismatch(mismatch_strategy)
                else:
                    passed_steps += 1
    except KeyboardInterrupt:
        _show_summary()
        exit(0)
