"""
 @file
 @brief Match the project profile to the first video clip placed on the timeline
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

import json
import os

import openshot

from qt_api import QObject, QTimer
from classes import info
from classes.app import get_app
from classes.logger import log
from classes.updates import UpdateInterface

SETTING = "auto-match-profile"
PROJECT_FLAG = "profile_user_selected"

# 29.97 is stored as 30000/1001 or 2997/100; 30 vs 29.97 must still differ
FPS_TOLERANCE = 0.005
RATIO_TOLERANCE = 0.01


def is_video_source(data):
    """Moving video with a usable frame rate (not an image, audio, album art, or text)."""
    if not isinstance(data, dict):
        return False
    if data.get("media_type") != "video" or data.get("type") == "QtTextReader":
        return False
    if data.get("has_single_image") or not data.get("has_video"):
        return False
    fps = data.get("fps") or {}
    if not fps.get("num") or not fps.get("den"):
        return False
    return bool(data.get("width")) and bool(data.get("height"))


def source_profile(data):
    """An (uninstalled) profile describing a video's own settings."""
    profile = openshot.Profile()
    profile.SetJson(json.dumps(data))
    ratio = profile.info.display_ratio
    if ratio.num == 1 and ratio.den == 1:
        # Some files report a 1:1 display ratio; calculate it from the size and pixel ratio
        profile.info.display_ratio = openshot.Fraction(
            round(profile.info.width * profile.info.pixel_ratio.ToFloat()), profile.info.height)
        profile.info.display_ratio.Reduce()
    return profile


def installed_profiles():
    for folder in (info.USER_PROFILES_PATH, info.PROFILES_PATH):
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isdir(path):
                continue
            try:
                yield openshot.Profile(path)
            except RuntimeError:
                continue


def _ratio(fraction):
    return fraction.num / fraction.den if fraction.den else 0.0


def rank(source, candidate):
    """Sort key: frame rate, then aspect ratio, then scan type and pixel shape, then resolution.
    An all-zero key is an exact match."""
    s, c = source.info, candidate.info
    fps_gap = abs(c.fps.ToFloat() - s.fps.ToFloat())
    aspect_gap = abs(_ratio(c.display_ratio) - _ratio(s.display_ratio))
    shape = int(bool(c.interlaced_frame) != bool(s.interlaced_frame)) + \
        int(abs(_ratio(c.pixel_ratio) - _ratio(s.pixel_ratio)) > RATIO_TOLERANCE)
    return (
        0 if fps_gap <= FPS_TOLERANCE else fps_gap,
        0 if aspect_gap <= RATIO_TOLERANCE else aspect_gap,
        shape,
        abs(c.width * c.height - s.width * s.height),
        abs(c.width - s.width) + abs(c.height - s.height),
    )


def best_profile(data, candidates=None):
    """The installed profile for a video's reader data, as (profile, exact).
    Returns (None, False) for anything that isn't a moving video."""
    if not is_video_source(data):
        return None, False
    source = source_profile(data)
    best_key, best = None, None
    for candidate in installed_profiles() if candidates is None else candidates:
        key = rank(source, candidate)
        if best_key is None or key < best_key:
            best_key, best = key, candidate
    if best is None:
        return None, False
    return best, not any(best_key)


def same_settings(profile, project):
    """Whether a profile already matches the project's size, frame rate and aspect ratio."""
    fps = project.get("fps") or {}
    ratio = project.get("display_ratio") or {}
    pixel = project.get("pixel_ratio") or {}
    p = profile.info
    return bool(p.width == project.get("width") and p.height == project.get("height")
                and fps and abs(p.fps.ToFloat() - fps["num"] / fps["den"]) <= FPS_TOLERANCE
                and (not ratio or abs(_ratio(p.display_ratio) - ratio["num"] / ratio["den"]) <= RATIO_TOLERANCE)
                and (not pixel or abs(_ratio(p.pixel_ratio) - pixel["num"] / pixel["den"]) <= RATIO_TOLERANCE))


def project_profile(project):
    """The project's current settings as a profile (to restore them later)."""
    profile = openshot.Profile()
    profile.SetJson(json.dumps({key: project.get(key) for key in (
        "width", "height", "fps", "display_ratio", "pixel_ratio")}))
    profile.info.description = project.get("profile") or ""
    return profile


class ProfileAutoMatch(QObject, UpdateInterface):
    """Matches the project profile to the first video clip placed on the timeline,
    unless the user picked a profile by hand in this project."""

    NOTICE_KEY = "profile_match"
    NOTICE_SECONDS = 12

    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.pending = None
        self.previous = None
        self.matched = None
        self.apply_timer = QTimer(self)
        self.apply_timer.setSingleShot(True)
        self.apply_timer.timeout.connect(self.apply_pending)
        self.notice_timer = QTimer(self)
        self.notice_timer.setSingleShot(True)
        self.notice_timer.setInterval(self.NOTICE_SECONDS * 1000)
        self.notice_timer.timeout.connect(self.dismiss)

    @staticmethod
    def enabled():
        app = get_app()
        return bool(app.get_settings().get(SETTING)) and not app.project.get(PROJECT_FLAG)

    def changed(self, action):
        if action.type != "insert" or not action.key or action.key[0] != "clips" or self.pending:
            return
        app = get_app()
        if getattr(app.updates, "_is_processing_history", False):
            return
        clip = action.values if isinstance(action.values, dict) else {}
        if not is_video_source(clip.get("reader")) or not self.enabled():
            return
        clip_id = clip.get("id")
        for other in app.project.get("clips") or []:
            if other.get("id") != clip_id and is_video_source(other.get("reader")):
                return
        # Apply after the drop (or paste) that inserted this clip has finished
        self.pending = clip_id
        self.apply_timer.start(0)

    def apply_pending(self):
        if getattr(getattr(self.window, "timeline", None), "_drag_preview_items", None):
            self.apply_timer.start(100)
            return
        clip_id, self.pending = self.pending, None
        project = get_app().project
        clip = next((c for c in project.get("clips") or [] if c.get("id") == clip_id), None)
        if not clip or not self.enabled():
            return
        profile, exact = best_profile(clip.get("reader"))
        if not profile or same_settings(profile, project):
            return
        log.info("Matching project profile to clip %s: %s (%s)", clip_id, profile.info.description,
                 "exact" if exact else "closest")
        self.previous = project_profile(project)
        self.matched = profile.info.description
        self.window.actionProfile_trigger(profile, user_selected=False)
        self.show_notice(clip, profile, exact)

    def show_notice(self, clip, profile, exact):
        from windows.notifications import NotificationBanner, notification_area
        _ = get_app()._tr
        name = os.path.basename((clip.get("reader") or {}).get("path", "")) or _("this clip")
        if exact:
            message = _("Project set to %(profile)s to match %(clip)s.")
        else:
            message = _("Project set to %(profile)s, the closest match to %(clip)s.")
        banner = NotificationBanner(
            self.window, message % {"profile": profile.info.description, "clip": name}, _("Undo"),
            self.undo, self.dismiss, _, icon_name="tool-profile")
        notification_area(self.window).add(self.NOTICE_KEY, banner)
        self.notice_timer.start()

    def undo(self):
        """Restore the previous profile, and keep it (as if picked by hand)."""
        previous, self.previous = self.previous, None
        self.dismiss()
        if previous and get_app().project.get("profile") == self.matched:
            self.window.actionProfile_trigger(previous, user_selected=True)

    def dismiss(self):
        self.notice_timer.stop()
        if hasattr(self.window, "notification_area"):
            self.window.notification_area.remove(self.NOTICE_KEY)
