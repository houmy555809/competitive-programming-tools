import lib
class FloatRelError(lib.Validator):
    def __init__(self):
        super(FloatRelError, self).__init__()
    def judge(self, filea, fileb):
        tokenA = tokenB = "0"
        tokenId = 0
        while tokenA is not None and tokenB is not None:
            numA = float(tokenA)
            numB = float(tokenB)
            if abs(numA - numB) > max(1, min(numA, numB)) * 1e-5:
                lib.report("WA", "Number %d differ. Read %s and %s. Difference is %.5f." % (tokenId, tokenA, tokenB, abs(numA - numB)))
                return
            tokenA = self.filea_read_token('0.')
            tokenB = self.fileb_read_token('0.')
        if (tokenA is not None) != (tokenB is not None):
            lib.report("WA", "Extra token in file %s." % ('A' if tokenA is not None else 'B'))
            return
        lib.report("AC", "Accepted.")
        return
judger = FloatRelError()
judger()