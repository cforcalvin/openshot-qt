"""
 @file
 @brief Live switching between audio output devices, including following the system default
 @author Jonathan Thomas <jonathan@openshot.org>

 @section LICENSE

 Copyright (c) 2008-2026 OpenShot Studios, LLC
 (http://www.openshotstudios.com). This file is part of
 OpenShot Video Editor (http://www.openshot.org), an open-source project
 dedicated to delivering high quality video editing and animation solutions
 to the world.

 OpenShot Video Editor is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 OpenShot Video Editor is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with OpenShot Library.  If not, see <http://www.gnu.org/licenses/>.
 """

import threading

import openshot

from qt_api import QObject, pyqtSignal, pyqtSlot
from classes.app import get_app
from classes.logger import log

POLL_SECONDS = 1.5
DEVICE_SETTING = "playback-audio-device"
EXPLICIT_SETTING = "playback-audio-device-explicit"


def parse_device_setting(value):
    """Split a "name||type" setting into (name, type); a blank name means the system default."""
    parts = (value or "").split("||")
    name = parts[0].strip()
    device_type = parts[1].strip() if len(parts) == 2 else ""
    return name, device_type


def format_device_setting(name, device_type):
    return f"{name}||{device_type}" if name else ""


def same_device(first, second):
    """Whether two device names refer to the same output.

    CoreAudio/JUCE sometimes reports a short name ("Speakers") for the full
    device ("MacBook Air Speakers"), so treat matching suffixes as the same.
    """
    a = (first or "").strip().casefold()
    b = (second or "").strip().casefold()
    if a == b:
        return True
    if not a or not b:
        return False
    return a.endswith(" " + b) or b.endswith(" " + a)


def _normalize_snapshot(snapshot):
    """Stable form for change detection (device list order from CoreAudio can flip)."""
    default = snapshot.get("default") or ("", "")
    outputs = tuple(sorted(
        ((name or "", device_type or "") for name, device_type in (snapshot.get("outputs") or [])),
        key=lambda item: (item[0].casefold(), item[1].casefold()),
    ))
    return (default[0] or "", default[1] or ""), outputs


def _device_connected(name, outputs):
    return any(same_device(name, output) for output, _ in (outputs or []))


def migrate_device_setting(settings):
    """Older versions saved whichever device opened (which libopenshot then ignored).
    Only devices the user picks are honored now, so reset to following the system default once."""
    if settings.get(EXPLICIT_SETTING):
        return
    if settings.get(DEVICE_SETTING):
        log.info("Resetting audio output to follow the system default (was %s)", settings.get(DEVICE_SETTING))
        settings.set(DEVICE_SETTING, "")


class AudioOutputMonitor(QObject):
    """Polls the system's audio outputs on a background thread, reporting changes."""

    # {"default": (name, type), "outputs": [(name, type), ...]}
    outputs_changed = pyqtSignal(object)

    def __init__(self, interval=POLL_SECONDS, parent=None):
        super().__init__(parent)
        self._interval = interval
        self._stop = threading.Event()
        self._thread = None
        self._last = None

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, name="audio-output-monitor", daemon=True)
            self._thread.start()

    def stop(self):
        self._stop.set()

    @staticmethod
    def poll():
        default = openshot.AudioDevices().getDefaultOutput()
        outputs = [(name, device_type) for name, device_type in openshot.AudioDevices().getNames()]
        return {"default": (default.get_name(), default.get_type()), "outputs": outputs}

    def _run(self):
        while not self._stop.is_set():
            try:
                snapshot = self.poll()
            except Exception:
                log.debug("Failed to poll audio outputs", exc_info=True)
                snapshot = None
            if snapshot is not None:
                normalized = _normalize_snapshot(snapshot)
                if normalized != self._last:
                    self._last = normalized
                    try:
                        self.outputs_changed.emit(snapshot)
                    except RuntimeError:
                        # QObject deleted during shutdown
                        return
            self._stop.wait(self._interval)


class AudioOutputController(QObject):
    """Keeps the preview player on the preferred audio output, switching live as devices come and go.

    A blank preference follows the system default output. A chosen device is used whenever it is
    connected, falling back to the system default while it is not."""

    # (name, type) of the device that is open now
    active_device_changed = pyqtSignal(str, str)
    # Monitor snapshot, see AudioOutputMonitor.outputs_changed
    outputs_changed = pyqtSignal(object)

    def __init__(self, player, monitor=None, parent=None):
        super().__init__(parent)
        self.player = player
        self.monitor = monitor or AudioOutputMonitor(parent=self)
        self.monitor.outputs_changed.connect(self.on_outputs_changed)
        self.active = None
        self.snapshot = None
        self._requested = None
        self._failed = None

    def stop(self):
        self.monitor.stop()

    def preferred(self):
        return parse_device_setting(get_app().get_settings().get(DEVICE_SETTING))

    def follows_system_default(self):
        return not self.preferred()[0]

    def outputs(self):
        """Known output devices (polling now if the monitor has not reported yet)."""
        if self.snapshot is None:
            try:
                self.snapshot = AudioOutputMonitor.poll()
            except Exception:
                log.debug("Failed to list audio outputs", exc_info=True)
                return []
        return list(self.snapshot["outputs"])

    def is_connected(self, name):
        return _device_connected(name, self.outputs())

    def target(self):
        """The device that should be open now, and how to request it from libopenshot
        (a blank request name opens the system default)."""
        name, device_type = self.preferred()
        if name and (self.snapshot is None or self.is_connected(name)):
            return (name, device_type), (name, device_type)
        default = self.snapshot["default"] if self.snapshot else ("", "")
        return default, ("", "")

    def select(self, name, device_type):
        """Use a specific output device (blank name = follow the system default)."""
        settings = get_app().get_settings()
        settings.set(DEVICE_SETTING, format_device_setting(name, device_type))
        settings.set(EXPLICIT_SETTING, True)
        self._failed = None
        self.reconcile()

    @pyqtSlot(str, str)
    def on_device_opened(self, name, device_type):
        """The player (re)opened an audio device."""
        first = self.active is None
        self.active = (name, device_type)
        requested, self._requested = self._requested, None
        if requested and requested[0] and not same_device(requested[0], name):
            # Don't keep retrying a device that won't open, until that device's
            # connectivity actually changes (list reorder must not clear this).
            log.warning("Requested audio output %s, but %s opened", requested[0], name)
            self._failed = requested
        elif requested and not requested[0]:
            # Following the system default: accept whatever CoreAudio opened,
            # even when getDefaultOutput()'s name disagrees (e.g. "Speakers").
            self._failed = None
        self.active_device_changed.emit(name, device_type)
        if first:
            self.monitor.start()
        self.reconcile()

    @pyqtSlot(object)
    def on_outputs_changed(self, snapshot):
        previous = self.snapshot
        self.snapshot = snapshot
        if self._failed:
            was = _device_connected(self._failed[0], (previous or {}).get("outputs"))
            now = _device_connected(self._failed[0], snapshot.get("outputs"))
            if was != now:
                self._failed = None
        self.outputs_changed.emit(snapshot)
        self.reconcile()

    def reconcile(self):
        """Switch devices if the open one is not the one that should be open."""
        if self.active is None or self._requested is not None:
            return
        target, request = self.target()
        if not target[0]:
            return
        if same_device(target[0], self.active[0]):
            return
        if self._failed and same_device(target[0], self._failed[0]):
            return
        log.info("Switching audio output from %s to %s", self.active[0] or "(none)", target[0])
        self._requested = target
        self.player.SetAudioDevice(*request)
