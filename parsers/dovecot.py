import re
from parsers.base import Parser


class DovecotImapLoginParser(Parser):
    def parse(self, entry):
        if entry.tag == "dovecot" and \
                entry.content[0:18] == "imap-login: Login:":
            m = self.kv_re.findall(entry.content)

            attrs = dict(m)
            attrs['user'] = attrs['user'].strip('<>')
            return "Dovecot IMAP login for {user} from {rip}".format(**attrs)


class DovecotErrorParser(Parser):
    def parse(self, entry):
        if entry.tag == "dovecot" and \
                "command startup failed" in entry.content:
            # TODO: combine multiple entries into one alert sent periodically
            failed_re = re.compile(r'service\((?P<service>[\w\-/]+)\)')
            m = failed_re.search(entry.content)

            service = m.group('service')
            return "Dovecot command startup failed for service {}".format(
                service)
