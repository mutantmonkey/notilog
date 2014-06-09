import importlib
import kombu
import logging
import socketserver
from notilog import parsers
from notilog.logentry import LogEntry

logger = logging.getLogger(__name__)


class PagerSyslogServer(socketserver.UDPServer):
    def __init__(self, config, server_address, *args,
                 **kwargs):
        self.queue_name = config['queue']
        self.init_broker(config['broker'])
        self.load_parsers(config['parsers'])

        super().__init__(server_address, PagerHandler, *args, **kwargs)

    def init_broker(self, broker_uri):
        self.broker_conn = kombu.Connection(broker_uri)
        self.broker_conn.ensure_connection(errback=self.errback)

        # use queue_name as queue, exchange, and routing key to match
        # SimpleQueue interface
        self.producer = kombu.Producer(self.broker_conn)
        self.exchange = kombu.Exchange(self.queue_name, type='direct')
        self.queue = kombu.Queue(self.queue_name, self.exchange,
                                 routing_key=self.queue_name)

    def errback(self, exc, interval):
        logger.error("{exc}; retry in {interval} seconds".format(
            exc=exc, interval=interval))

    def load_parsers(self, modules):
        self.parsers = []
        for item in modules:
            components = item.split('.')
            path = '.' + '.'.join(components[:-1])
            module = importlib.import_module(path, package='notilog.parsers')
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
                            declare=[self.server.queue])
                    return
