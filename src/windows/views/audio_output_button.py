"""
 @file
 @brief Video toolbar button for picking the preview's audio output device
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

from qt_api import Qt, QSize, QMenu, QToolButton, QActionGroup

from classes.app import get_app
from classes.audio_output import same_device
from windows.preview_icons import preview_icon


class AudioOutputButton(QToolButton):
    """Shows the active audio output and switches between outputs from a menu."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("audioOutputButton")
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setIconSize(QSize(20, 20))
        self.setPopupMode(QToolButton.InstantPopup)
        self.setAccessibleName(get_app()._tr("Audio output"))
        self.controller = None
        self.menu = QMenu(self)
        self.menu.aboutToShow.connect(self.rebuild_menu)
        self.setMenu(self.menu)
        self.refresh_icon()
        self.update_tooltip()

    def refresh_icon(self):
        self.setIcon(preview_icon("tool-preview-volume"))

    def set_controller(self, controller):
        self.controller = controller
        controller.active_device_changed.connect(self.update_tooltip)
        self.update_tooltip()

    def update_tooltip(self, *_args):
        _ = get_app()._tr
        active = self.controller.active if self.controller else None
        if active and active[0]:
            self.setToolTip(_("Audio output: %s") % active[0])
        else:
            self.setToolTip(_("Audio output"))

    def rebuild_menu(self):
        _ = get_app()._tr
        self.menu.clear()
        if not self.controller:
            return
        preferred_name, _preferred_type = self.controller.preferred()
        active = self.controller.active or ("", "")
        outputs = self.controller.outputs()
        group = QActionGroup(self.menu)

        default_name = self.controller.snapshot["default"][0] if self.controller.snapshot else ""
        label = _("System Default (%s)") % default_name if default_name else _("System Default")
        action = self.menu.addAction(label)
        action.setCheckable(True)
        action.setChecked(not preferred_name)
        action.triggered.connect(lambda: self.controller.select("", ""))
        group.addAction(action)
        self.menu.addSeparator()

        for name, device_type in outputs:
            text = name
            if same_device(name, active[0]):
                text = _("%s (playing)") % name
            action = self.menu.addAction(text)
            action.setCheckable(True)
            action.setChecked(bool(preferred_name) and same_device(name, preferred_name))
            action.triggered.connect(lambda _checked=False, n=name, t=device_type: self.controller.select(n, t))
            group.addAction(action)

        if preferred_name and not self.controller.is_connected(preferred_name):
            # Chosen device is disconnected; the system default plays until it returns
            action = self.menu.addAction(_("%s (disconnected)") % preferred_name)
            action.setCheckable(True)
            action.setChecked(True)
            action.setEnabled(False)
            group.addAction(action)
