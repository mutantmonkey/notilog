import re


class Parser(object):
    def __init__(self):
        self.kv_re = re.compile(r'([A-Za-z0-9]+)=([^,]+),')
