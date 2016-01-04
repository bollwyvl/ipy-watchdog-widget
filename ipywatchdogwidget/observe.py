import argparse
import time
import sys
from uuid import uuid4

import zmq
from jupyter_client.session import Session

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def observe(path, poll_interval, port, recursive,
            session_key, model_id):
    session = str(uuid4())

    class WidgetHandler(FileSystemEventHandler):
        def __init__(self, *args, **kwargs):
            super(WidgetHandler, self).__init__(*args, **kwargs)

            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.XREQ)
            self.socket.linger = 1000
            self.socket.connect("tcp://127.0.0.1:%s" % port)
            self.session = Session(key=session_key.encode())

        def on_any_event(self, event):
            msg = self.msg(event)
            self.session.send(self.socket, msg)

        def msg(self, event):
            return {
                "buffers": [],
                "channel": "shell",
                "metadata": {},
                "parent_header": {},
                "header": {
                    "msg_id": str(uuid4()),
                    "username": "watchdog",
                    "session": session,
                    "msg_type": "comm_msg",
                    "version": "5.0"
                },
                "content": {
                    "comm_id": model_id,
                    "data": {
                        "method": "custom",
                        "content": {
                            "event": event.event_type,
                            "is_directory": event.is_directory,
                            "src_path": event.src_path,
                            "dest_path": getattr(event,
                                                 "dest_path",
                                                 None)
                        }
                    },
                },
            }

    observer = Observer()
    event_handler = WidgetHandler()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def make_parser():
    parser = argparse.ArgumentParser(
        description='Watch a file, report back to the kernel')

    parser.add_argument(
        '--model-id',
        default=u"2a2ef4874eaa4dcfa9d07b6f7cb892dd",
        type=str,
        help='the model id of the widget')
    parser.add_argument(
        '--path',
        default=".",
        type=str,
        help='the directory to watch')
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=1,
        help='time in seconds to wait between polling')
    parser.add_argument(
        '--port',
        type=int,
        default=62091,
        help='port to connect over ZMQ')
    parser.add_argument(
        '--recursive',
        type=bool,
        default=False,
        help='whether to recurse into subdirectories')
    parser.add_argument(
        '--session-key',
        type=str,
        default="b0cb4961-0908-4ae6-843c-bc77312821a9",
        help='the session key of the user')

    return parser


if __name__ == "__main__":
    kwargs = make_parser().parse_args().__dict__
    observe(**kwargs)
