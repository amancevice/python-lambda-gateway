import logging
from pkg_resources import (get_distribution, DistributionNotFound)


def set_stream_logger(name, level=logging.DEBUG, format_string=None):
    """
    Adapted from boto3.set_stream_logger()
    """
    if format_string is None:
        format_string = \
            '%(addr)s - - [%(asctime)s] %(levelname)s - %(message)s'

    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(format_string, '%-d/%b/%Y %H:%M:%S')
    adapter = logging.LoggerAdapter(logger, dict(addr='::1'))
    logger.setLevel(level)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return adapter


def _version():
    """
    Helper to get package version.
    """
    try:
        return get_distribution(__name__).version
    except DistributionNotFound:  # pragma: no cover
        return None


__version__ = _version()

logger = set_stream_logger(__name__)
