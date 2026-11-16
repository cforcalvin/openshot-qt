"""
 @file
 @brief Unit tests for live audio output switching
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

from classes import audio_output
from classes.audio_output import (
    AudioOutputController, migrate_device_setting, parse_device_setting, format_device_setting,
    same_device)

SPEAKERS = ("MacBook Air Speakers", "CoreAudio")
SPEAKERS_SHORT = ("Speakers", "CoreAudio")
AIRPODS = ("AirPods Pro", "CoreAudio")


class _Settings:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value


def _snapshot(default, *outputs):
    return {"default": default, "outputs": list(outputs)}


class DeviceSettingTests(unittest.TestCase):
    def test_parse_and_format(self):
        self.assertEqual(parse_device_setting("AirPods Pro||CoreAudio"), AIRPODS)
        self.assertEqual(parse_device_setting("PulseAudio Sound Server"), ("PulseAudio Sound Server", ""))
        self.assertEqual(parse_device_setting("||"), ("", ""))
        self.assertEqual(parse_device_setting(None), ("", ""))
        self.assertEqual(format_device_setting(*AIRPODS), "AirPods Pro||CoreAudio")
        self.assertEqual(format_device_setting("", "CoreAudio"), "")

    def test_short_coreaudio_name_matches_full_device(self):
        self.assertTrue(same_device("MacBook Air Speakers", "Speakers"))
        self.assertTrue(same_device("Speakers", "MacBook Air Speakers"))
        self.assertFalse(same_device("AirPods Pro", "Speakers"))
        self.assertFalse(same_device("USB Speakers", "MacBook Air Speakers"))

    def test_auto_saved_device_is_reset_once(self):
        settings = _Settings({"playback-audio-device": "MacBook Air Speakers||CoreAudio"})
        migrate_device_setting(settings)
        self.assertEqual(settings.get("playback-audio-device"), "")

    def test_chosen_device_is_kept(self):
        settings = _Settings({"playback-audio-device": "AirPods Pro||CoreAudio",
                              "playback-audio-device-explicit": True})
        migrate_device_setting(settings)
        self.assertEqual(settings.get("playback-audio-device"), "AirPods Pro||CoreAudio")


class AudioOutputControllerTests(unittest.TestCase):
    def setUp(self):
        self.settings = _Settings({"playback-audio-device": ""})
        app = SimpleNamespace(get_settings=lambda: self.settings)
        patcher = patch.object(audio_output, "get_app", return_value=app)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.player = Mock()
        self.monitor = Mock()
        self.controller = AudioOutputController(self.player, monitor=self.monitor)

    def test_follows_system_default_when_headphones_connect(self):
        self.controller.on_device_opened(*SPEAKERS)
        self.monitor.start.assert_called_once_with()
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS))
        self.player.SetAudioDevice.assert_not_called()

        self.controller.on_outputs_changed(_snapshot(AIRPODS, SPEAKERS, AIRPODS))
        self.player.SetAudioDevice.assert_called_once_with("", "")

        # Waits for the switch to finish before requesting another
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS))
        self.assertEqual(self.player.SetAudioDevice.call_count, 1)

        # Headphones opened, then disconnect: back to the speakers
        self.controller.on_device_opened(*AIRPODS)
        self.assertEqual(self.player.SetAudioDevice.call_count, 2)
        self.controller.on_device_opened(*SPEAKERS)
        self.assertEqual(self.player.SetAudioDevice.call_count, 2)

    def test_chosen_device_stays_put_and_falls_back_while_disconnected(self):
        self.settings.set("playback-audio-device", "AirPods Pro||CoreAudio")
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS, AIRPODS))
        self.controller.on_device_opened(*AIRPODS)
        self.player.SetAudioDevice.assert_not_called()

        # Disconnected: play through the system default
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS))
        self.player.SetAudioDevice.assert_called_once_with("", "")
        self.controller.on_device_opened(*SPEAKERS)

        # Reconnected: back to the chosen device, even though it isn't the default
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS, AIRPODS))
        self.player.SetAudioDevice.assert_called_with(*AIRPODS)

    def test_select_saves_choice_and_switches(self):
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS, AIRPODS))
        self.controller.on_device_opened(*SPEAKERS)
        self.controller.select(*AIRPODS)
        self.assertEqual(self.settings.get("playback-audio-device"), "AirPods Pro||CoreAudio")
        self.assertTrue(self.settings.get("playback-audio-device-explicit"))
        self.player.SetAudioDevice.assert_called_once_with(*AIRPODS)

        self.controller.on_device_opened(*AIRPODS)
        self.controller.select("", "")
        self.assertEqual(self.settings.get("playback-audio-device"), "")
        self.player.SetAudioDevice.assert_called_with("", "")

    def test_device_that_fails_to_open_is_not_retried(self):
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS, AIRPODS))
        self.controller.on_device_opened(*SPEAKERS)
        self.controller.select(*AIRPODS)
        self.controller.on_device_opened(*SPEAKERS)
        self.assertEqual(self.player.SetAudioDevice.call_count, 1)

        # Reordering or unrelated devices must not clear the failure
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, AIRPODS, SPEAKERS, ("BlackHole 2ch", "CoreAudio")))
        self.assertEqual(self.player.SetAudioDevice.call_count, 1)

        # Disconnect then reconnect the failed device allows another attempt
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS))
        self.controller.on_device_opened(*SPEAKERS)
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS, AIRPODS))
        self.assertEqual(self.player.SetAudioDevice.call_count, 2)

    def test_short_speaker_name_matches_preferred_speakers(self):
        self.settings.set("playback-audio-device", "MacBook Air Speakers||CoreAudio")
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS))
        self.controller.on_device_opened(*SPEAKERS_SHORT)
        self.player.SetAudioDevice.assert_not_called()

    def test_system_default_accepts_short_open_name(self):
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS))
        self.controller.on_device_opened(*SPEAKERS_SHORT)
        self.player.SetAudioDevice.assert_not_called()
        # Default request that opens a short name must not thrash
        self.controller.on_outputs_changed(_snapshot(SPEAKERS, SPEAKERS))
        self.player.SetAudioDevice.assert_not_called()

    def test_nothing_happens_before_a_device_opens(self):
        self.controller.on_outputs_changed(_snapshot(AIRPODS, SPEAKERS, AIRPODS))
        self.player.SetAudioDevice.assert_not_called()
        self.monitor.start.assert_not_called()


if __name__ == "__main__":
    unittest.main()
