import lib
class CaseInsensitive(lib.Validator):
    def __init__(self):
        super(CaseInsensitive, self).__init__()
    def judge(self, filea, fileb):
        contenta = self.filea_read().split("\n")
        contentb = self.fileb_read().split("\n")
        for i in range(len(contenta) - 1, -1, -1):
            if contenta[i].rstrip() == "":
                del contenta[i]
            else:
                break
        for i in range(len(contentb) - 1, -1, -1):
            if contentb[i].rstrip() == "":
                del contentb[i]
            else:
                break
        common_len = min(len(contenta), len(contentb))
        for i in range(common_len):
            if contenta[i].rstrip().lower() != contentb[i].rstrip().lower():
                lib.report("WA", "Wrong answer at line %d: Read '%s' and '%s'." % (i + 1, lib.escapeStr(contenta[i].rstrip()), lib.escapeStr(contentb[i].rstrip())))
                return
        if len(contenta) > len(contentb):
            lib.report("WA", "Program 2 answer too short.")
            return
        elif len(contenta) < len(contentb):
            lib.report("WA", "Program 1 answer too short.")
            return
        lib.report("AC", "Accepted.")
        return
judger = CaseInsensitive()
judger()