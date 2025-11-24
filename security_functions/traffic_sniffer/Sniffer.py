from datetime import datetime, timezone
import logging, os, queue, threading
from nfstream import NFStreamer

LOGGER = logging.getLogger(__name__)

MONITORED_DEVICE       = str(os.getenv('MONITORED_DEVICE',       'router'))
SNIFFER_INTERFACE      = str(os.getenv('SNIFFER_INTERFACE',      'eth1'  ))
SNIFFER_CAPTURE_FILTER = str(os.getenv('SNIFFER_CAPTURE_FILTER', ''      ))
SNIFFER_PROMISCUOUS    = str(os.getenv('SNIFFER_PROMISCUOUS',    'true'  )).upper() == 'TRUE'
FLOW_IDLE_TIMEOUT      = int(os.getenv('FLOW_IDLE_TIMEOUT',      '30'    ))
FLOW_ACTIVE_TIMEOUT    = int(os.getenv('FLOW_ACTIVE_TIMEOUT',    '30'    ))

class Sniffer(threading.Thread):
    def __init__(self, message_queue : queue.Queue) -> None:
        super().__init__(daemon=True)
        self.message_queue = message_queue
        self.terminate = threading.Event()

    def stop(self) -> None:
        self.terminate.set()

    def run(self) -> None:
        try:
            MSG = 'Creating NFStreamer on interface "{:s}" (filter="{:s}")...'
            LOGGER.info(MSG.format(str(SNIFFER_INTERFACE), str(SNIFFER_CAPTURE_FILTER)))
            streamer = NFStreamer(
                source=SNIFFER_INTERFACE, bpf_filter=SNIFFER_CAPTURE_FILTER,
                idle_timeout=FLOW_IDLE_TIMEOUT, active_timeout=FLOW_ACTIVE_TIMEOUT,
                promiscuous_mode=SNIFFER_PROMISCUOUS
            )

            flows = iter(streamer)
            while not self.terminate.is_set():
                flow = next(flows)
                timestamp = datetime.now(timezone.utc).isoformat()
                self.message_queue.put((flow, timestamp))
        except Exception:
            LOGGER.exception('Unhandled Exception')
