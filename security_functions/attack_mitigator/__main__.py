import logging, signal, sys, threading
from .Manager import Manager

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s')
LOGGER = logging.getLogger(__name__)

def main() -> int:
    terminate = threading.Event()

    def signal_handler(signum, frame):  # pylint: disable=unused-argument
        LOGGER.warning('Terminate signal received.')
        terminate.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    manager = Manager()

    LOGGER.info('Starting...')
    try:
        manager.start()
    except Exception:
        LOGGER.exception('Unable to start Manager.')
        return -1

    LOGGER.info('Running...')
    while not terminate.wait(timeout=1.0):
        pass

    LOGGER.info('Stopping...')
    try:
        manager.stop()
    except Exception:
        LOGGER.exception('Unable to stop Manager.')
        return -2

    LOGGER.info('Shutdown complete.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
