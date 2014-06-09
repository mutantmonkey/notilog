from .base import Parser


class SudoParser(Parser):
    def parse(self, entry):
        if entry.tag == "sudo":
            pass
