#!/usr/bin/python3

import lib


class PerToken(lib.Validator):
    def judge(self, filea, fileb):
        token_a = token_b = ""
        token_id = 0
        while token_a is not None and token_b is not None:
            if token_a != token_b:
                lib.report("WA", f"Token {token_id} differ. Read {token_a} and {token_b}.")
                return
            token_a = self.filea_read_token()
            token_b = self.fileb_read_token()
        if (token_a is not None) != (token_b is not None):
            lib.report("WA", f"Extra token in file {'A' if token_a is not None else 'B'}.")
            return
        lib.report("AC", "Accepted.")


judger = PerToken()
judger()
