import re
from .base import Parser


class DovecotImapLoginParser(Parser):
    def parse(self, entry):
        if entry.tag == "dovecot" and \
                entry.content[0:18] == "imap-login: Login:":
            m = self.kv_re.findall(entry.content)

            attrs = dict(m)
            attrs['user'] = attrs['user'].strip('<>')
            return "{hostname}: Dovecot IMAP login for {user} from {rip}".\
                format(hostname=entry.hostname, **attrs)


class DovecotErrorParser(Parser):
    def parse(self, entry):
        if entry.tag == "dovecot" and \
                "command startup failed" in entry.content:
            # TODO: combine multiple entries into one alert sent periodically
            failed_re = re.compile(r'service\((?P<service>[\w\-/]+)\)')
            m = failed_re.search(entry.content)

            service = m.group('service')
            return "{hostname}: Dovecot command startup failed for service "\
                "{service}".format(hostname=entry.hostname, service=service)
