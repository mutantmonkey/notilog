#!/usr/bin/python3

import kombu
import logging
import importlib
import os.path
import re
import socketserver
import yaml

logger = logging.getLogger(__name__)
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


class PagerSyslogServer(socketserver.UDPServer):
    def __init__(self, broker_uri, queue_name, *args, **kwargs):
        self.queue_name = queue_name
        self.init_broker(broker_uri)

        super().__init__(*args, **kwargs)

    def init_broker(self, broker_uri):
        self.broker_conn = kombu.Connection(broker_uri)
        self.broker_conn.ensure_connection(errback=self.errback)

        # use queue_name as queue, exchange, and routing key to match
        # SimpleQueue interface
        self.producer = kombu.Producer(self.broker_conn)
        self.exchange = kombu.Exchange(self.queue_name, type='direct')
        self.pager_queue = kombu.Queue(self.queue_name, self.exchange,
                                       routing_key=self.queue_name)

    def errback(self, exc, interval):
        logger.error("{exc}; retry in {interval} seconds".format(
            exc=exc,
            interval=interval))

    def load_parsers(self, modules):
        self.parsers = []
        for item in modules:
            components = ['parsers'] + item.split('.')
            path = '.'.join(components[:-1])
            module = importlib.import_module(path)
            class_ = getattr(module, components[-1])
            self.parsers.append(class_())

    def close(self):
        self.broker_conn.release()


class PagerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip().decode('utf-8')
        entry = LogEntry(data)
        if entry.tag is not None:
            for parser in self.server.parsers:
                result = parser.parse(entry)
                if result is not None:
                    publish = self.server.broker_conn.ensure(
                        self.server.producer, self.server.producer.publish,
                        errback=self.server.errback, max_retries=3)
                    publish(result, exchange=self.server.exchange,
                            routing_key=self.server.queue_name,
                            declare=[self.server.pager_queue])
                    return



if __name__ == '__main__':
    try:
        import xdg.BaseDirectory
        configpath = xdg.BaseDirectory.load_first_config('notilog/config.yml')
    except:
        configpath = os.path.expanduser('~/.config/notilog/config.yml')
    config = yaml.safe_load(open(configpath))

    s = PagerSyslogServer(config['broker'], config['queue'],
                          ('localhost', 6514), PagerHandler)
    s.load_parsers(['dovecot.DovecotImapLoginParser',
                    'dovecot.DovecotErrorParser',
                    'sshd.SshdLoginParser'])
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        s.close()
