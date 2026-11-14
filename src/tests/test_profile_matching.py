"""
 @file
 @brief Unit tests for matching the project profile to the first video clip
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

import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from classes import profile_matching
from classes.profile_matching import ProfileAutoMatch, best_profile, is_video_source, same_settings
from classes.updates import UpdateAction


def reader(width=1920, height=1080, num=30, den=1, **changes):
    data = dict(media_type="video", type="FFmpegReader", has_video=True, has_single_image=False,
                width=width, height=height, fps=dict(num=num, den=den), path="/media/%dx%d.mp4" % (width, height),
                pixel_ratio=dict(num=1, den=1), display_ratio=dict(num=1, den=1), interlaced_frame=False)
    data.update(changes)
    return data


def clip(clip_id, data):
    return dict(id=clip_id, reader=data)


class _Project:
    def __init__(self, **values):
        self.values = dict(width=1280, height=720, fps=dict(num=30, den=1), display_ratio=dict(num=16, den=9),
                           pixel_ratio=dict(num=1, den=1), profile="HD 720p 30 fps", profile_user_selected=False,
                           clips=[])
        self.values.update(values)

    def get(self, key):
        return self.values.get(key)


class BestProfileTests(unittest.TestCase):
    def check(self, data, description, exact):
        profile, found_exact = best_profile(data)
        self.assertEqual(profile.info.description, description)
        self.assertEqual(found_exact, exact)

    def test_exact_installed_profiles(self):
        self.check(reader(3840, 2160, 60), "4K UHD 2160p 60 fps", True)
        self.check(reader(1080, 1920, 30000, 1001), "FHD Vertical 1080p 29.97 fps", True)

    def test_29_97_variants_are_the_same_rate(self):
        self.check(reader(1920, 1080, 2997, 100), "FHD 1080p 29.97 fps", True)

    def test_closest_keeps_frame_rate_and_aspect_ratio(self):
        # Variable frame rate phone footage reports an average rate
        self.check(reader(1080, 1920, 5996, 100), "FHD Vertical 1080p 59.94 fps", False)
        self.check(reader(1170, 2532, 30, 1), "FHD Vertical 1080p 30 fps", False)
        self.check(reader(1000, 1000, 30, 1), "HD Square 1080p 30 fps", False)

    def test_non_video_sources_are_rejected(self):
        for data in (reader(media_type="image"), reader(has_single_image=True), reader(has_video=False),
                     reader(fps=dict(num=0, den=1)), reader(type="QtTextReader"), reader(media_type="audio"),
                     None):
            with self.subTest(data=data):
                self.assertFalse(is_video_source(data))
                self.assertEqual(best_profile(data), (None, False))

    def test_same_settings(self):
        profile, _exact = best_profile(reader(1280, 720, 30))
        self.assertTrue(same_settings(profile, _Project()))
        self.assertFalse(same_settings(profile, _Project(fps=dict(num=60, den=1))))


class ProfileAutoMatchTests(unittest.TestCase):
    def setUp(self):
        self.project = _Project()
        self.settings = {"auto-match-profile": True}
        self.updates = SimpleNamespace(_is_processing_history=False)
        app = SimpleNamespace(project=self.project, updates=self.updates,
                              get_settings=lambda: SimpleNamespace(get=self.settings.get), _tr=lambda text: text)
        patcher = patch.object(profile_matching, "get_app", return_value=app)
        patcher.start()
        self.addCleanup(patcher.stop)
        notice = patch.object(ProfileAutoMatch, "show_notice")
        self.show_notice = notice.start()
        self.addCleanup(notice.stop)
        self.window = Mock(timeline=SimpleNamespace(_drag_preview_items=[]))
        self.controller = ProfileAutoMatch(None)
        self.controller.window = self.window

    def place(self, new_clip):
        self.project.values["clips"].append(new_clip)
        self.controller.changed(UpdateAction("insert", ["clips"], new_clip))
        if self.controller.pending:
            self.controller.apply_timer.stop()
            self.controller.apply_pending()

    def applied(self):
        return [c.args[0].info.description for c in self.window.actionProfile_trigger.call_args_list]

    def test_first_video_clip_sets_the_profile(self):
        self.place(clip("C1", reader(1080, 1920, 60)))
        self.assertEqual(self.applied(), ["FHD Vertical 1080p 60 fps"])
        self.assertEqual(self.window.actionProfile_trigger.call_args.kwargs, {"user_selected": False})
        self.show_notice.assert_called_once()

    def test_only_the_first_video_clip_counts(self):
        self.project.values["clips"].append(clip("C0", reader(3840, 2160, 60)))
        self.place(clip("C1", reader(1080, 1920, 60)))
        self.window.actionProfile_trigger.assert_not_called()

    def test_images_and_audio_do_not_count_or_consume_the_trigger(self):
        self.place(clip("I1", reader(media_type="image")))
        self.place(clip("A1", reader(media_type="audio", has_video=False)))
        self.window.actionProfile_trigger.assert_not_called()
        self.place(clip("C1", reader(1920, 1080, 25)))
        self.assertEqual(self.applied(), ["FHD PAL 1080p 25 fps"])

    def test_undo_and_redo_are_ignored(self):
        self.updates._is_processing_history = True
        self.place(clip("C1", reader(1080, 1920, 60)))
        self.window.actionProfile_trigger.assert_not_called()

    def test_hand_picked_profile_and_setting_are_respected(self):
        self.project.values["profile_user_selected"] = True
        self.place(clip("C1", reader(1080, 1920, 60)))
        self.project.values.update(profile_user_selected=False, clips=[])
        self.settings["auto-match-profile"] = False
        self.place(clip("C2", reader(1080, 1920, 60)))
        self.window.actionProfile_trigger.assert_not_called()

    def test_matching_profile_is_left_alone(self):
        self.place(clip("C1", reader(1280, 720, 30)))
        self.window.actionProfile_trigger.assert_not_called()
        self.show_notice.assert_not_called()

    def test_waits_for_the_drag_preview_and_skips_removed_clips(self):
        self.window.timeline._drag_preview_items = [{"type": "clip"}]
        new_clip = clip("C1", reader(1080, 1920, 60))
        self.project.values["clips"].append(new_clip)
        self.controller.changed(UpdateAction("insert", ["clips"], new_clip))
        self.controller.apply_timer.stop()
        self.controller.apply_pending()
        self.assertEqual(self.controller.pending, "C1")
        self.controller.apply_timer.stop()
        self.window.timeline._drag_preview_items = []
        self.project.values["clips"].clear()
        self.controller.apply_pending()
        self.window.actionProfile_trigger.assert_not_called()

    def test_undo_restores_the_previous_profile_as_a_choice(self):
        self.place(clip("C1", reader(1080, 1920, 60)))
        self.project.values["profile"] = "FHD Vertical 1080p 60 fps"
        self.controller.undo()
        previous = self.window.actionProfile_trigger.call_args
        self.assertEqual(previous.args[0].info.description, "HD 720p 30 fps")
        self.assertEqual(previous.args[0].info.width, 1280)
        self.assertEqual(previous.kwargs, {"user_selected": True})


class ProfileMatchWindowTests(unittest.TestCase):
    def test_first_clip_undo_and_hand_picked_profile_in_real_window(self):
        source = Path(__file__).resolve().parents[1]
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen", QT_QUICK_BACKEND="software",
                   PYTHONPATH=os.pathsep.join(filter(None, (
                       str(source), os.environ.get("PYTHONPATH", ""), str(source.parent)))))
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("profile_match_smoke.py"))],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout[-12000:])
        self.assertIn("PROFILE_MATCH_PASSED", result.stdout)


if __name__ == "__main__":
    unittest.main()
