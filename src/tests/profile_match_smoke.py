"""Verify the project profile follows the first video clip in the real main window."""
import json
import os
import tempfile
import time
import traceback
import unittest

import openshot

root = tempfile.mkdtemp(prefix="openshot-profile-match-")
original_expanduser = os.path.expanduser
os.path.expanduser = lambda path: root if path == "~" else original_expanduser(path)

from classes.app import OpenShotApp
from classes import version
from classes.query import File
from qt_api import QCoreApplication, QPointF, QTimer

version.get_current_Version = lambda: None
app = OpenShotApp([], mode="unittest")
app.settings.set("tutorial_enabled", False)
app.settings.set("send_metrics", False)
checks = unittest.TestCase()
passed = False


def write_video(path, width, height, fps):
    writer = openshot.FFmpegWriter(path)
    writer.SetVideoOptions(True, "mpeg4", openshot.Fraction(fps, 1), width, height,
                           openshot.Fraction(1, 1), False, False, 2000000)
    writer.Open()
    for number in range(1, 13):
        writer.WriteFrame(openshot.Frame(number, width, height, "#336699"))
    writer.Close()


def import_file(path):
    native = openshot.Clip(path)
    source = File()
    source.data = json.loads(native.Reader().Json())
    source.data.update(path=path, media_type="video", name=os.path.basename(path))
    source.save()
    return source


def wait_for(condition, seconds=10):
    deadline = time.time() + seconds
    while time.time() < deadline:
        QCoreApplication.processEvents()
        if condition():
            return True
        time.sleep(0.02)
    return condition()


def verify():
    global passed
    try:
        window = app.window
        project = app.project
        layer = project.get("layers")[-1]["number"]
        original = project.get("profile")
        checks.assertFalse(project.get("profile_user_selected"))

        vertical = os.path.join(root, "vertical.mp4")
        write_video(vertical, 1080, 1920, 60)
        window.timeline.addClip(import_file(vertical).id, QPointF(1., 0), layer, call_manual_move=False)
        checks.assertTrue(wait_for(lambda: project.get("width") == 1080), project.get("profile"))
        checks.assertEqual((project.get("height"), project.get("fps")), (1920, {"num": 60, "den": 1}))
        checks.assertEqual(project.get("profile"), "FHD Vertical 1080p 60 fps")
        checks.assertFalse(project.get("profile_user_selected"))
        banner = window.notification_area.banners.get("profile_match")
        checks.assertIsNotNone(banner)
        checks.assertIn("FHD Vertical 1080p 60 fps", banner.message.text())

        # Undo keeps the previous profile as the user's choice
        banner.primary.click()
        checks.assertTrue(wait_for(lambda: project.get("profile") == original), project.get("profile"))
        checks.assertTrue(project.get("profile_user_selected"))
        checks.assertNotIn("profile_match", window.notification_area.banners)

        # With a hand-picked profile, a new first clip leaves it alone
        for item in list(project.get("clips")):
            app.updates.delete(["clips", {"id": item["id"]}])
        wide = os.path.join(root, "wide.mp4")
        write_video(wide, 1920, 1080, 25)
        window.timeline.addClip(import_file(wide).id, QPointF(1., 0), layer, call_manual_move=False)
        wait_for(lambda: False, 1)
        checks.assertEqual(project.get("profile"), original)
        passed = True
        print("PROFILE_MATCH_PASSED", flush=True)
    except Exception:
        traceback.print_exc()
    finally:
        app.project.has_unsaved_changes = False
        app.exit(0)


checks.assertTrue(app.gui())
QTimer.singleShot(3000, verify)
app.exec_()
raise SystemExit(0 if passed else 1)
