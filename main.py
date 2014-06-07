#!/usr/bin/python3

import re
import socketserver

log_re = re.compile(r'^(<(?P<priority>\d+)>)?'
                    r'(?P<timestamp>\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+'
                    r'(?P<hostname>\w+)\s+(?P<tag>[\w\-\[\]/]+):\s+'
                    r'(?P<content>.*)$')


class LogEntry(object):
    def __init__(self, data):
        m = log_re.match(data)
        if m:
            self.priority = m.group('priority')
            self.timestamp = m.group('timestamp')
            self.hostname = m.group('hostname')
            self.tag = m.group('tag')
            self.content = m.group('content')
            self.raw = data
        else:
            self.priority = None
            self.timestamp = None
            self.hostname = None
            self.tag = None
            self.content = None
            self.raw = data

    def __repr__(self):
        return self.raw


class PagerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip().decode('utf-8')
        entry = LogEntry(data)

        kv_re = re.compile(r'([A-Za-z0-9]+)=([^,]+),')

        if entry.tag is None:
            pass
        elif entry.tag == "sudo":
            # TODO: combine multiple entries into one alert sent periodically
            pass
        elif entry.tag[0:4] == "sshd" and entry.content[0:8] == "Accepted":
            ssh_re = re.compile(
                r'^Accepted (?P<method>[\w\-/]+) for (?P<user>\w+) from '
                r'(?P<ip>[0-9a-f:\.]+) port (?P<port>\d+) (?P<protocol>\w+)')
            m = ssh_re.match(entry.content)

            attrs = m.groupdict()
            print("ssh login for {user} from {ip} using {method}".format(
                **attrs))
        elif entry.tag == "dovecot" and \
                entry.content[0:18] == "imap-login: Login:":
            m = kv_re.findall(entry.content)

            attrs = dict(m)
            attrs['user'] = attrs['user'].strip('<>')
            print("dovecot imap login for {user} from {rip}".format(**attrs))
        elif entry.tag == "dovecot" and \
                "command startup failed" in entry.content:
            # TODO: combine multiple entries into one alert sent periodically
            failed_re = re.compile(r'service\((?P<service>[\w\-/]+)\)')
            m = failed_re.search(entry.content)

            service = m.group('service')
            print("dovecot command startup failed for service {}".format(
                service))

if __name__ == '__main__':
    s = socketserver.UDPServer(('localhost', 6514), PagerHandler)
    s.serve_forever()
