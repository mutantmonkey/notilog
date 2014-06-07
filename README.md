# notilog

notilog ("naughty log") lets you know about naughty things that happen in your
logs. It acts as a syslog server that you can configure your local syslog
daemon to forward messages to, and then it looks for events in your logs based
on a set of plugins. If the plugin returns a response, the response is placed
in a queue to be delivered by whatever paging glue you choose to write.

It's in early stages of development right now, so that last bit above about
placing the response into a queue isn't quite true yet.
