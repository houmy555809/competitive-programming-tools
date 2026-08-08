#!/usr/bin/python3

import lib


class CharByChar(lib.Validator):
    def judge(self, filea, fileb):
        content_a = self.filea_read().rstrip("\n")
        content_b = self.fileb_read().rstrip("\n")
        if len(content_a) != len(content_b):
            lib.report("WA", f"The length of the two files differ. Sizes are ({len(content_a)} and {len(content_b)}).")
            return
        for i in range(len(content_a)):
            if content_a[i] != content_b[i]:
                lib.report("WA", f"Char {i} differ. Read {lib.escape(content_a[i])} and {lib.escape(content_b[i])}.")
                return
        lib.report("AC", "Accepted.")


judger = CharByChar()
judger()
