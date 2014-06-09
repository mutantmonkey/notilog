#!/usr/bin/python3

import os.path
import yaml
from notilog import server

if __name__ == '__main__':
    try:
        import xdg.BaseDirectory
        configpath = xdg.BaseDirectory.load_first_config('notilog/config.yml')
    except:
        configpath = os.path.expanduser('~/.config/notilog/config.yml')
    config = yaml.safe_load(open(configpath))

    s = server.PagerSyslogServer(config)
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        s.close()
