"""
 @file
 @brief Unit tests for syncing settings with the open audio device
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

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from windows.preview_thread import PlayerWorker, PreviewParent


def _player(sample_rate="44100.0", name="AirPods Pro", device_type="CoreAudio"):
    player = Mock()
    player.GetAudioDeviceGeneration.return_value = 3
    player.GetError.return_value = ""
    player.GetDefaultSampleRate.return_value = sample_rate
    player.GetCurrentAudioDevice.return_value = SimpleNamespace(
        get_name=lambda: name, get_type=lambda: device_type)
    return player


class _Settings:
    def __init__(self, values):
        self.values = dict(values)

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value


class CheckAudioDeviceTests(unittest.TestCase):
    def test_worker_only_emits_device_info(self):
        worker = SimpleNamespace(player=_player(), error_found=Mock(), audio_device_checked=Mock(),
                                 _audio_device_generation=None)
        app = Mock(side_effect=AssertionError("worker thread must not touch app state"))
        with patch("windows.preview_thread.get_app", app):
            PlayerWorker.CheckAudioDevice(worker)
        worker.audio_device_checked.emit.assert_called_once_with({
            "sample_rate": 44100.0,
            "device_name": "AirPods Pro",
            "device_type": "CoreAudio",
        })
        worker.error_found.emit.assert_not_called()
        self.assertEqual(worker._audio_device_generation, 3)

    def test_gui_thread_applies_sample_rate_and_reports_device(self):
        settings = _Settings({"default-samplerate": 48000, "playback-audio-device": ""})
        project = Mock(has_unsaved_changes=False)
        project.get.return_value = 48000
        updates = Mock()
        app = SimpleNamespace(get_settings=lambda: settings, project=project, updates=updates)
        preview = SimpleNamespace(audio_device_opened=Mock())
        with patch("windows.preview_thread.get_app", return_value=app):
            PreviewParent.onAudioDeviceChecked(preview, {
                "sample_rate": 44100.0,
                "device_name": "AirPods Pro",
                "device_type": "CoreAudio",
            })
        self.assertEqual(settings.get("default-samplerate"), 44100)
        updates.update_untracked.assert_called_once_with(["sample_rate"], 44100)
        self.assertFalse(project.has_unsaved_changes)
        # The open device is reported, while the saved choice (follow default) is kept
        preview.audio_device_opened.emit.assert_called_once_with("AirPods Pro", "CoreAudio")
        self.assertEqual(settings.get("playback-audio-device"), "")

    def test_undetected_rate_leaves_settings_alone(self):
        settings = _Settings({"default-samplerate": 48000, "playback-audio-device": "Speakers||CoreAudio"})
        project = Mock(has_unsaved_changes=False)
        project.get.return_value = 48000
        updates = Mock()
        app = SimpleNamespace(get_settings=lambda: settings, project=project, updates=updates)
        preview = SimpleNamespace(audio_device_opened=Mock())
        with patch("windows.preview_thread.get_app", return_value=app):
            PreviewParent.onAudioDeviceChecked(preview, {
                "sample_rate": float("nan"),
                "device_name": "Speakers",
                "device_type": "CoreAudio",
            })
        self.assertEqual(settings.get("default-samplerate"), 48000)
        updates.update_untracked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
