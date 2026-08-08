#!/usr/bin/python3

import lib


class Noip(lib.Validator):
    def judge(self, filea, fileb):
        content_a = self.filea_read().split("\n")
        content_b = self.fileb_read().split("\n")
        while content_a and content_a[-1].rstrip() == "":
            content_a.pop()
        while content_b and content_b[-1].rstrip() == "":
            content_b.pop()
        common_len = min(len(content_a), len(content_b))
        for i in range(common_len):
            if content_a[i].rstrip() != content_b[i].rstrip():
                lib.report("WA", f"Wrong answer at line {i + 1}: Read '{lib.escape_str(content_a[i].rstrip())}' and '{lib.escape_str(content_b[i].rstrip())}'.")
                return
        if len(content_a) > len(content_b):
            lib.report("WA", "Program B answer too short.")
            return
        if len(content_a) < len(content_b):
            lib.report("WA", "Program A answer too short.")
            return
        lib.report("AC", "Accepted.")


judger = Noip()
judger()
