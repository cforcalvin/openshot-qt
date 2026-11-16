"""
Timeline theme class for the Studio Dark Qt theme.

Derives from HumanityDarkTimelineTheme and overrides only what differs.

Frozen visual tokens (from Studio Dark mockup):
  surface0 #1C1C1E  surface1 #2C2C2E  surface2 #3A3A3C
  accent   #0A84FF  playhead #FABE0A  text #EBEBF5 / #8E8E93
  radii    clips/transitions 8px; tracks flush
"""

from qt_api import QColor

from themes.humanity.styles import HumanityDarkTimelineTheme
from windows.views.timeline_backend.theme import _icon


class StudioDarkTimelineTheme(HumanityDarkTimelineTheme):
    """Studio Dark timeline theme."""

    def __init__(self):
        super().__init__()

        self.track_size_presets = {
            "minimal": (24, 2), "compact": (36, 4), "relaxed": (64, 8),
        }

        # Preserve Studio Dark's established sizing and edge treatments.
        self.label_font_scale = 1.0
        self.clip.shadow_color = QColor("#000000")
        self.clip.shadow_blur = 10
        self.track.font_color = QColor("#FFFFFF")
        self.track.name_border_right_color = QColor()
        self.track.name_border_right_width = 0
        self.transition.border_radius = 6
        self.ruler.border_color = QColor("#ACACAC")
        self.ruler.font_color = QColor("#999999")

        # ── Timeline ──────────────────────────────────────────────────────
        self.background             = QColor("#1C1C1E")
        self.background2            = QColor()
        self.playhead_color         = QColor("#FABE0A")
        self.ruler_name_background  = QColor("#1C1C1E")
        self.ruler_name_background2 = QColor()
        self.scrollbar_track        = QColor("#1C1C1E")
        self.scrollbar_width        = 8
        self.keyframe_inactive_opacity       = 0.5
        self.keyframe_panel_property_bg      = QColor()
        self.keyframe_panel_row_border_color = QColor()
        self.keyframe_panel_curve_color      = QColor()
        self.keyframe_panel_marker_fill      = QColor()
        self.keyframe_panel_marker_border    = QColor()

        # ── Clip ──────────────────────────────────────────────────────────
        self.clip.background    = QColor("#2C2C2E")
        self.clip.background2   = QColor()
        self.clip.top_overlay   = QColor()      # gradient overlay disabled
        self.clip.top_overlay2  = QColor()
        self.clip.border_color  = QColor("#0A84FF")
        self.clip.border_radius = 6
        self.clip.height        = 48

        # ── Track ─────────────────────────────────────────────────────────
        self.track.background               = QColor("#3A3A3C")
        self.track.background2              = QColor()
        self.track.border_color             = QColor("#3A3A3C")
        self.track.border_radius            = 0
        self.track.height                   = 48
        self.track.name_background          = QColor("#2C2C2E")
        self.track.name_border_color        = QColor("#0A84FF")
        self.track.name_border_width        = 2
        self.track.name_border_top_color    = QColor("#2C2C2E")
        self.track.name_border_top_width    = 1
        self.track.name_border_bottom_color = QColor("#2C2C2E")
        self.track.name_border_bottom_width = 1
        self.track.name_radius_tl           = 0   # gradient overlay/radius disabled
        self.track.name_radius_bl           = 0
        self.track.name_top_overlay         = QColor()
        self.track.name_top_overlay2        = QColor()

        # ── Transition ────────────────────────────────────────────────────
        self.transition.height = 48

        # ── Ruler ─────────────────────────────────────────────────────────
        self.ruler.background  = QColor("#1C1C1E")
        self.ruler.background2 = QColor()

        # ── Icons ─────────────────────────────────────────────────────────
        _c = "themes/studio/images/"

        self.playhead_icon                      = _icon(_c + "playhead.svg")
        self.track_keyframe_panel_disabled_icon = _icon(_c + "track-keyframe-panel-show-disabled.svg")
        self.track_keyframe_panel_enabled_icon  = _icon(_c + "track-keyframe-panel-show-enabled.svg")
        self.track_keyframe_panel_hide_disabled_icon = _icon(_c + "track-keyframe-panel-hide-disabled.svg")
        self.track_keyframe_panel_hide_enabled_icon = _icon(_c + "track-keyframe-panel-hide-enabled.svg")
        self.keyframe_panel_add_icon            = _icon(_c + "keyframe-panel-add.svg")
        self.track_add_above_disabled_icon      = _icon(_c + "track-add-above-disabled.svg")
        self.track_add_above_enabled_icon       = _icon(_c + "track-add-above-enabled.svg")
        self.track_add_below_disabled_icon      = _icon(_c + "track-add-below-disabled.svg")
        self.track_add_below_enabled_icon       = _icon(_c + "track-add-below-enabled.svg")
        self.track_delete_disabled_icon         = _icon(_c + "track-delete-disabled.svg")
        self.track_delete_enabled_icon          = _icon(_c + "track-delete-enabled.svg")
        self.track_locked_disabled_icon         = _icon(_c + "track-locked-disabled.svg")
        self.track_locked_enabled_icon          = _icon(_c + "track-locked-enabled.svg")
        self.track_unlocked_disabled_icon       = _icon(_c + "track-unlocked-disabled.svg")
        self.track_unlocked_enabled_icon        = _icon(_c + "track-unlocked-enabled.svg")

        self.keyframe_toggle_off_icon = self.track_keyframe_panel_disabled_icon
        self.keyframe_toggle_on_icon  = self.track_keyframe_panel_enabled_icon
