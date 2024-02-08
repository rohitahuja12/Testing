import os

do_log_events = os.environ.get('LOG_EVENTS', False)

def get_event_logger(logger):
    def _inner(event):
        if do_log_events:
            logger.info(event)
    return _inner
