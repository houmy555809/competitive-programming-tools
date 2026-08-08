#!/usr/bin/python3

import lib


class FloatAbsError(lib.Validator):
    def judge(self, filea, fileb):
        token_a = token_b = "0"
        token_id = 0
        while token_a is not None and token_b is not None:
            num_a = float(token_a)
            num_b = float(token_b)
            if abs(num_a - num_b) > 1e-5:
                lib.report("WA", f"Number {token_id} differ. Read {token_a} and {token_b}. Difference is {abs(num_a - num_b):.5f}.")
                return
            token_a = self.filea_read_token("0.")
            token_b = self.fileb_read_token("0.")
        if (token_a is not None) != (token_b is not None):
            lib.report("WA", f"Extra token in file {'A' if token_a is not None else 'B'}.")
            return
        lib.report("AC", "Accepted.")


judger = FloatAbsError()
judger()
