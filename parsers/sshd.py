import re
from parsers.base import Parser


class SshdLoginParser(Parser):
    def parse(self, entry):
        if entry.tag[0:4] == "sshd" and entry.content[0:8] == "Accepted":
            ssh_re = re.compile(
                r'^Accepted (?P<method>[\w\-/]+) for (?P<user>\w+) from '
                r'(?P<ip>[0-9a-f:\.]+) port (?P<port>\d+) (?P<protocol>\w+)')
            m = ssh_re.match(entry.content)

            attrs = m.groupdict()
            return "SSH login for {user} from {ip} using {method}".format(
                **attrs)
