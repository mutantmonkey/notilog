#!/usr/bin/python3

import importlib
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
        if entry.tag is not None:
            for parser in self.server.parsers:
                result = parser.parse(entry)
                if result is not None:
                    print(result)
                    break


def load_parsers(modules):
    parsers = []
    for item in modules:
        components = ['parsers'] + item.split('.')
        path = '.'.join(components[:-1])
        module = importlib.import_module(path)
        class_ = getattr(module, components[-1])
        parsers.append(class_())
    return parsers


if __name__ == '__main__':
    s = socketserver.UDPServer(('localhost', 6514), PagerHandler)
    s.parsers = load_parsers(['dovecot.DovecotImapLoginParser',
                              'dovecot.DovecotErrorParser',
                              'sshd.SshdLoginParser'])
    s.serve_forever()
