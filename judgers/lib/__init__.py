import sys
from colorama import *

def report(status, desc):
    print(status, desc)
    exit(0)

def escape(char):
    if char in "abcdefghijklmnopqrtstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`~!@#$%^&*()-_+=[]{}|;:<>,./?":
        return char
    elif char in "\\\"\'":
        return "\\" + char
    else:
        return "<ASCII " + str(ord(char)) + ">"
def escapeStr(string):
    res = ""
    for i in string:
        res += escape(i)
    return res

def get_full_charset(abbrev_charset):
    mapping = {'a':"abcdefghijklmnopqrstuvwxyz", 'A':"ABCDEFGHIJKLMNOPQRSTUVWXYZ", '0':"0123456789", '.':"`~!@#$%^&*()-_+=[]{}/?\\\"\'", ',':"|;:,."}
    full_charset = ""
    for i in abbrev_charset:
        if i in mapping.keys():
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
        if char == None:
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
        self.buf_a = Buffer(self._filea_read())
        self.buf_b = Buffer(self._fileb_read())

    def _filea_read(self):
        with open(sys.argv[2], "r") as file:
            content = '\n'.join(file.readlines())
            file.close()
        return content
    
    def _fileb_read(self):
        with open(sys.argv[3], "r") as file:
            content = '\n'.join(file.readlines())
            file.close()
        return content
    
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
            self.judge(sys.argv[1], sys.argv[2])
        except Exception as err:
            report("UKE", "Validator returned error " + str(err))