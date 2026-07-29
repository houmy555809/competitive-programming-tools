import lib
class PerToken(lib.Validator):
    def __init__(self):
        super(PerToken, self).__init__()
    def judge(self, filea, fileb):
        tokenA = tokenB = ""
        tokenId = 0
        while tokenA is not None and tokenB is not None:
            if tokenA != tokenB:
                lib.report("WA", "Token %d differ. Read %s and %s." % (tokenId, tokenA, tokenB))
                return
            tokenA = self.filea_read_token()
            tokenB = self.fileb_read_token()
        if (tokenA is not None) != (tokenB is not None):
            lib.report("WA", "Extra token in file %s." % ('A' if tokenA is not None else 'B'))
            return
        lib.report("AC", "Accepted.")
        return
judger = PerToken()
judger()