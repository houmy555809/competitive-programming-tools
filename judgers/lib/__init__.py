import sys


def report(status, desc):
    print(status, desc)
    exit(0)


def escape(char):
    if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`~!@#$%^&*()-_+=[]{}|;:<>,./?":
        return char
    if char in "\\\"'":
        return "\\" + char
    return "<ASCII " + str(ord(char)) + ">"


def escape_str(string):
    res = ""
    for i in string:
        res += escape(i)
    return res


def get_full_charset(abbrev_charset):
    mapping = {
        "a": "abcdefghijklmnopqrstuvwxyz",
        "A": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "0": "0123456789",
        ".": "`~!@#$%^&*()-_+=[]{}/?\\\"'.",
        ",": "|;:,.",
    }
    full_charset = ""
    for i in abbrev_charset:
        if i in mapping:
            full_charset += mapping[i]
    return full_charset


class Buffer:
    def __init__(self, content):
        self.buf = content
        self.ptr = 0

    def read_all(self):
        return self.buf

    def read_char(self):
        if self.ptr == len(self.buf):
            return None
        res = self.buf[self.ptr]
        self.ptr += 1
        return res

    def read_token(self, charset):
        charset = get_full_charset(charset)
        char = None
        while self.ptr != len(self.buf):
            char = self.read_char()
            if char in charset:
                break
        if char is None:
            return None
        res = char
        while self.ptr != len(self.buf):
            char = self.read_char()
            if char not in charset:
                break
            res += char
        return res


class Validator:
    def __init__(self):
        self.buf_a = Buffer(self._file_a_read())
        self.buf_b = Buffer(self._file_b_read())

    def _file_a_read(self):
        with open(sys.argv[2], "r") as f:
            return f.read()

    def _file_b_read(self):
        with open(sys.argv[3], "r") as f:
            return f.read()

    def filea_read(self):
        return self.buf_a.read_all()

    def fileb_read(self):
        return self.buf_b.read_all()

    def filea_read_char(self):
        return self.buf_a.read_char()

    def fileb_read_char(self):
        return self.buf_b.read_char()

    def filea_read_token(self, charset = "aA0."):
        return self.buf_a.read_token(charset)

    def fileb_read_token(self, charset = "aA0."):
        return self.buf_b.read_token(charset)

    def __call__(self):
        try:
            self.judge(sys.argv[2], sys.argv[3])
        except Exception as err:
            report("UKE", f"Validator returned error {err}")
