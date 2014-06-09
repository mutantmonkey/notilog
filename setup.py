from setuptools import setup

setup(
    name="notilog",
    packages=["notilog", "notilog.parsers"],
    scripts=["notilog-server"],
    version="1.0",
    description="notilog lets you know about naughty things that happen in your logs.",
    license="ISC",
    author="mutantmonkey",
    author_email="notilog@mutantmonkey.in",
    url="https://github.com/mutantmonkey/notilog",
    install_requires=["amqp>=1.4.5", "kombu>=3.0.16", "PyYAML>=3.11"]
)
