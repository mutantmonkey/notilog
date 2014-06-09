import re

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
