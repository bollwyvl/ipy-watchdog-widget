import os
import sys
import subprocess
import glob
from fnmatch import fnmatch

import psutil

import traitlets
from ipywidgets import widgets
from IPython import get_ipython


class Watchdog(widgets.Widget):
    path = traitlets.CUnicode(".", sync=True)
    description = traitlets.CUnicode(sync=True)
    value = traitlets.Any(sync=True)
    recursive = traitlets.CBool(False, sync=True)
    watching = traitlets.CBool(False, sync=True)
    poll_interval = traitlets.CInt(1, sync=True)
    last_event = traitlets.Dict(sync=True)
    file = traitlets.CUnicode(sync=True)

    def __init__(self, *args, **kwargs):
        super(Watchdog, self).__init__(*args, **kwargs)

        self._wd_handlers = widgets.CallbackDispatcher()
        self._wd_observer = None
        self.on_msg(self._handle_wd_msg)

    def __del__(self):
        self.stop()
        super(Watchdog, self).__del__()

    def _handle_wd_msg(self, _, content, buffers):
        """ Be very careful here: inspecting the messages in the
            browser may be the only way to find problems
        """
        self.last_event = content
        event = content.get('event', None)
        if event is None:
            return
        if (not self.file) or fnmatch(content["src_path"], self.file):
            self._wd_handlers(self, content)

    def on_any(self, callback, remove=False):
        self._wd_handlers.register_callback(callback, remove=remove)

    def ls(self):
        return glob.glob(os.path.join(self.path, self.file or "*.*"))

    def touch(self, idx=0):
        os.utime(self.ls()[idx], None)

    def start(self):
        self.stop()

        ip = get_ipython()

        self._wd_observer = subprocess.Popen(
            map(str, [
                sys.executable,
                "-m",
                "ipywatchdogwidget.observe",
                "--model-id", self.model_id,
                "--path", os.path.abspath(self.path),
                "--poll-interval", self.poll_interval,
                "--port", ip.kernel._recorded_ports["shell"],
                "--recursive", self.recursive,
                "--session-key", ip.kernel.session.key.decode()
            ]),
            stderr=subprocess.STDOUT)
        self.watching = True

    def stop(self):
        if self._wd_observer:
            parent = psutil.Process(self._wd_observer.pid)
            [child.kill() for child in parent.children(recursive=True)]
            parent.kill()
            self._wd_observer = None
        self.watching = False
