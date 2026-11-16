"""
 @file
 @brief This file contains a theme's colors and UI dimensions
 @author Jonathan Thomas <jonathan@openshot.org>

 @section LICENSE

 Copyright (c) 2008-2024 OpenShot Studios, LLC
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

from qt_api import Qt
from qt_api import QIcon
from qt_api import QTabWidget, QWidget

from classes.info import PATH
from ..base import BaseTheme


class StudioDarkTheme(BaseTheme):
    def __init__(self, app):
        super().__init__(app)

        self.style_sheet = """
QToolTip, QLabel#razorHint {
    color: #F5F5F7;
    font-size: 12px;
    font-weight: normal;
    background-color: rgba(44, 44, 46, 235);
    border: 1px solid #636366;
    border-radius: 6px;
    margin: 0;
    min-width: 0;
    min-height: 0;
    padding: 2px 4px;
}

QMainWindow {
    background-color: #2C2C2E;
    color: #EBEBF5;
}

QWidget#tutorial {
    background-color: #2C2C2E;
    border: 1.2px solid #0A84FF;
    border-radius: 4px;
    padding: 20px;
}

QLabel#lblTutorialText {
    font-size: 14px;
}

QCheckBox#checkboxMetrics {
    font-size: 14px;
}

QWidget#tutorial QPushButton#NextTip {
    background-color: #3A3A3C;
    font-size: 12px;
}

QWidget#tutorial QPushButton#HideTutorial {
    font-size: 12px;
}


QDialog {
    background-color: #2C2C2E;
    color: #EBEBF5;
}

QLabel#lblMissingFileHint,
QLabel#lblMissingFilePath {
    color: #8E8E93;
}

QFrame#recordingCard {
    background-color: rgba(20, 31, 48, 190);
    border: 1px solid rgba(70, 134, 230, 110);
    border-radius: 8px;
}
QFrame#recordingCard[checked="true"] {
    border: 2px solid #0A84FF;
    background-color: rgba(26, 58, 105, 170);
}
QFrame#recordingCard[available="false"] {
    border: 1px solid rgba(80, 91, 110, 90);
    background-color: rgba(20, 25, 34, 120);
}
QLabel#recordingCardIcon {
    color: #AEAEB2;
    font-size: 22px;
}
QLabel#recordingCardTitle {
    color: #F5F5F7;
    font-size: 14px;
    font-weight: 700;
}
QLabel#recordingCardSubtitle {
    color: #8E8E93;
    font-size: 11px;
}
QFrame#recordingSection {
    background-color: rgba(13, 24, 38, 165);
    border: 1px solid rgba(83, 105, 134, 95);
    border-radius: 8px;
}
QFrame#recordingSection[active="true"] {
    border: 1px solid rgba(70, 141, 255, 125);
}
QFrame#recordingSection[active="false"] {
    color: #8E8E93;
    background-color: rgba(15, 20, 28, 95);
}
QLabel#recordingSectionIcon {
    color: #AEAEB2;
    font-size: 16px;
}
QLabel#recordingSectionTitle {
    color: #F5F5F7;
    font-weight: 700;
}
QPushButton#recordingAdvancedLink {
    color: #0A84FF;
    border: none;
    padding: 0;
    text-align: right;
}
QPushButton#recordingAdvancedLink:hover {
    color: #EBEBF5;
    text-decoration: underline;
}
QPushButton#recordingSegment {
    border: 1px solid rgba(83, 105, 134, 120);
    border-radius: 6px;
    padding: 7px 10px;
    color: #EBEBF5;
    background-color: rgba(14, 25, 40, 170);
}
QPushButton#recordingSegment[position="left"] {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}
QPushButton#recordingSegment[position="right"] {
    border-left: none;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}
QPushButton#recordingSegment:checked {
    color: #D1D1D6;
    border: 1px solid #0A84FF;
    background-color: rgba(40, 94, 170, 135);
}

QWidget#Simple, QWidget#Advanced, QWidget#exportResult, QWidget#PreferencePanel {
    background-color: #1C1C1E;
    border: none;
}

QScrollArea {
    border: none;
}

QTabWidget {
    border: none;
}

QMenuBar {
    background-color: #3A3A3C;
    color: #EBEBF5;
    padding: 0px;
    border: none;
}

QMenuBar::item {
    padding: 6px 10px;
    background: transparent;
}

QMenuBar::item:selected {
    background-color: #48484A;
    color: #ffffff;
}

QMenu {
    background-color: #1C1C1E;
    color: #EBEBF5;
    padding: 6px;
    padding-left: 8px;
    padding-right: 8px;
    min-width: 40px;
    border: 1.2px solid #0A84FF;
    border-radius: 3px 3px;
}

QMenu::item {
    padding: 6px 18px 6px 22px;
}

QMenu::item:checked {
    padding: 6px 18px 6px 22px;
}

QMenu::indicator {
    width: 12px;
    height: 12px;
}

QMenu::item:selected:enabled {
    background-color: #2C2C2E;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #8E8E93;
}

QMenu::separator {
    height: 8px;
    background-color: #1C1C1E;
}

QToolBar#toolBar {
    background-color: #3A3A3C;
    spacing: 0px;
    padding: 0px;
    border: none;
}

QToolBar#toolBar QToolButton {
    background-color: #3A3A3C;
    color: #EBEBF5;
    padding-top: 9px;
    padding-bottom: 9px;
    padding-left: 7px;
    padding-right: 7px;
    border: 1px solid transparent;
}

QToolBar#toolBar QToolButton:hover {
    background-color: #48484A;
}

QToolBar QToolButton:hover,
QDialog#sourcePreviewDialog QToolButton:hover {
    background-color: #2C2C2E;
}

QToolBar QToolButton:pressed {
    background-color: #2C2C2E;
}

QToolBar#filesToolbar,
QToolBar#transitionsToolbar,
QToolBar#effectsToolbar {
    background-color: transparent;
    spacing: 4px;
    padding: 2px;
    border: none;
}

QToolBar#filesToolbar QToolButton,
QToolBar#transitionsToolbar QToolButton,
QToolBar#effectsToolbar QToolButton {
    background-color: #1C1C1E;
    color: #EBEBF5;
    border-radius: 3px;
    padding: 2px 5px;
    border: 1px solid transparent;
}

QToolBar#filesToolbar QToolButton:hover,
QToolBar#transitionsToolbar QToolButton:hover,
QToolBar#effectsToolbar QToolButton:hover {
    background-color: #2C2C2E;
}

QToolBar#filesToolbar QToolButton:checked,
QToolBar#transitionsToolbar QToolButton:checked,
QToolBar#effectsToolbar QToolButton:checked {
    background-color: #3A3A3C;
}

QToolBar#filesToolbar QToolButton:focus,
QToolBar#transitionsToolbar QToolButton:focus,
QToolBar#effectsToolbar QToolButton:focus {
    border: 1px solid #64B5FF;
    background-color: #3A3A3C;
}


QToolBar#timelineToolbar {
    background-color: #2C2C2E;
    spacing: 0px;
    padding: 0px;
    border: none;
}

QToolBar#timelineToolbar QToolButton {
    color: #EBEBF5;
    background-color: #1C1C1E;
    padding: 7px;
    margin-bottom: 4px;
    margin-right: 5px;
    margin-left: 5px;
    border-radius: 4px;
    border: 1px solid transparent;
}

QToolBar#timelineToolbar QToolButton:hover {
    background-color: #3A3A3C;
}


QToolBar#timelineToolbar QToolButton:checked {
    background-color: #3A3A3C;
}

QToolBar#toolBar QToolButton:focus {
    border: 1px solid #64B5FF;
    background-color: #48484A;
}

QToolBar#timelineToolbar QToolButton:focus:!checked {
    border: 1px solid #64B5FF;
    background-color: #1C1C1E;
}

QToolBar#timelineToolbar QToolButton:checked:focus {
    border: 1px solid #64B5FF;
    background-color: #3A3A3C;
}

QToolBar#timelineToolbar QToolButton:pressed {
    background-color: #545456;
}

QToolBar#toolBar QToolButton:pressed {
    background-color: #545456;
}

QToolBar#filesToolbar QToolButton:pressed,
QToolBar#transitionsToolbar QToolButton:pressed,
QToolBar#effectsToolbar QToolButton:pressed {
    background-color: #48484A;
}

QToolBar#toolBar QToolButton:hover {
    background-color: #48484A;
}

QToolBar#videoToolbar QToolButton,
QDialog#sourcePreviewDialog QToolButton {
    border: 1px solid transparent;
}

QToolBar#videoToolbar QToolButton:focus,
QDialog#sourcePreviewDialog QToolButton:focus {
    border: 1px solid #64B5FF;
    background-color: #3A3A3C;
}

QToolBar#videoToolbar QToolButton:pressed,
QDialog#sourcePreviewDialog QToolButton:pressed {
    background-color: #48484A;
}

QFrame#textStyleBar {
    background-color: rgba(25, 35, 50, 238);
    border: 1px solid rgba(83, 105, 134, 150);
    border-radius: 8px;
    qproperty-iconColor: #EBEBF5;
}
QFrame#textStyleBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 3px;
}
QFrame#textStyleBar QToolButton:hover {
    background-color: #3A3A3C;
}
QFrame#textStyleBar QToolButton:checked {
    background-color: rgba(40, 94, 170, 150);
    border: 1px solid #0A84FF;
}
QFrame#textStyleBar QComboBox,
QFrame#textStyleBar QSpinBox {
    background-color: #121212;
    border-radius: 4px;
    padding: 3px 6px;
    min-height: 18px;
}
QFrame#textStyleBar QSpinBox {
    padding-right: 20px;
}
QFrame#textStyleDivider {
    background-color: rgba(83, 105, 134, 150);
    border: none;
}

QDialog#textStyleDialog {
    background-color: #2C2C2E;
}
QDialog#textStyleDialog QLabel {
    color: #EBEBF5;
    background-color: transparent;
}
QDialog#textStyleDialog QLabel#textStylePreview {
    background-color: #000000;
    border: 1px solid #3A3A3C;
    border-radius: 6px;
}
QFrame#textStyleSection {
    background-color: #1C1C1E;
    border: 1px solid #3A3A3C;
    border-radius: 8px;
}
QDialog#textStyleDialog QLabel#textStyleHeading {
    color: #F5F5F7;
    font-weight: 700;
}
QFrame#textStyleRule {
    background-color: #3A3A3C;
    border: none;
}
QPlainTextEdit#textStyleEditor {
    background-color: #121212;
    color: #F5F5F7;
    border: 1px solid #3A3A3C;
    border-radius: 6px;
    padding: 1px 4px;
}
QPlainTextEdit#textStyleEditor:focus {
    border-color: #0A84FF;
}
QPlainTextEdit#textStyleEditor:disabled {
    color: #EBEBF5;
}
QAbstractSpinBox#textStyleSpin {
    background-color: #121212;
    color: #F5F5F7;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 3px 22px 3px 8px;
}
QAbstractSpinBox#textStyleSpin:focus {
    border-color: #0A84FF;
}
QAbstractSpinBox#textStyleSpin::up-arrow,
QAbstractSpinBox#textStyleSpin::down-arrow {
    width: 15px;
    height: 15px;
}
QToolButton#textStyleSwatch {
    background-color: #121212;
    border: 1px solid #3A3A3C;
    border-radius: 4px;
    padding: 0px;
}
QToolButton#textStyleSwatch:hover {
    border-color: #0A84FF;
}
QPushButton#textStyleLink {
    background-color: transparent;
    color: #EBEBF5;
    border: none;
    padding: 8px 6px;
}
QPushButton#textStyleLink:hover,
QPushButton#textStyleLink:focus {
    color: #ffffff;
    background-color: transparent;
}
QDialog#textStyleDialog QPushButton#acceptButton {
    padding: 8px 20px;
}

QPushButton#acceptButton,
QDialog#sourcePreviewDialog QPushButton[dialogRole="primary"]:enabled,
QWidget#exportResult QPushButton[dialogRole="primary"]:enabled {
    padding: 8px 16px 8px 12px;
    border-radius: 4px;
    background-color: #0A84FF;
    color: #FFFFFF;
}

QPushButton#acceptButton:hover,
QDialog#sourcePreviewDialog QPushButton[dialogRole="primary"]:enabled:hover,
QWidget#exportResult QPushButton[dialogRole="primary"]:enabled:hover {
    background-color: #0077ED;
}

QPushButton#acceptButton:focus,
QPushButton#acceptButton:default,
QDialog#sourcePreviewDialog QPushButton[dialogRole="primary"]:enabled:focus,
QWidget#exportResult QPushButton[dialogRole="primary"]:enabled:focus {
    background-color: #0A84FF;
}

QPushButton {
    padding: 8px 16px 8px 12px;
    border-radius: 4px;
    background-color: #2C2C2E;
    color: #EBEBF5;
}

QPushButton:hover {
    background-color: #3A3A3C;
}

QPushButton:focus {
    background-color: #3A3A3C;
}

QDialog#animatedTitle QPushButton:disabled,
QDialog#animatedTitle QPushButton#acceptButton:disabled,
QDialog#exportDialog QPushButton#acceptButton:disabled {
    background-color: #2C2C2E;
    color: #8E8E93;
}

QDialog#animatedTitle QPushButton#cancelButton {
    background-color: #3A3A3C;
}

QDialog#animatedTitle QPushButton#cancelButton:enabled:hover {
    background-color: #3A3A3C;
}

QDialog#animatedTitle QPushButton#cancelButton:enabled:pressed {
    background-color: #48484A;
}

QWidget#settingsContainer {
    background-color: #1C1C1E;
}

QWidget#scrollAreaWidgetContents {
    background-color: #1C1C1E;
}

QPushButton#dock-close-button {
    image: url({PATH}themes/studio/images/dock-close.svg);
    padding: 0px;
    padding-top: 2px;
    padding-bottom: 2px;
    margin: 0px;
    margin-right: 16px;
    width: 16px;
    height: 16px;
}
QPushButton#dock-float-button {
    image: url({PATH}themes/studio/images/dock-float.svg);
    padding: 0px;
    padding-top: 2px;
    padding-bottom: 2px;
    margin: 0px;
    width: 16px;
    height: 16px;
}

QPushButton#dock-close-button,
QPushButton#dock-float-button {
    border: 1px solid transparent;
    background: transparent;
}

QPushButton#dock-close-button:hover,
QPushButton#dock-float-button:hover,
QPushButton#dock-close-button:pressed,
QPushButton#dock-float-button:pressed,
QPushButton#dock-close-button:focus,
QPushButton#dock-float-button:focus {
    background: transparent;
}

QPushButton#dock-close-button:focus,
QPushButton#dock-float-button:focus {
    border: 1px solid #64B5FF;
    outline: none;
}

QLabel#dock-title-label {
    color: #EBEBF5;
    font-weight: 500;
    min-height: 20px;
    padding: 9px 0px 0px 0px;
    margin: 0px 16px 8px 16px;
    border-bottom: 1px solid transparent;
}

QLabel#dock-title-handle {
    padding-left: 16px;
    qproperty-pixmap: url({PATH}themes/studio/images/dock-move.svg);
}

QDockWidget {
    background-color: #1C1C1E;
    titlebar-close-icon: url({PATH}themes/studio/images/dock-close.svg);
    titlebar-normal-icon: url({PATH}themes/studio/images/dock-float.svg);
    color: #EBEBF5;
    font-weight: 500;
    padding: 16px;
}

QDockWidget QWidget {
    border: none;
}

QLabel#dock-title-label[focusWithin="true"] {
    border-bottom: 1px solid #64B5FF;
}

QTabBar[dockFocusTabs="true"]::tab {
    border-bottom: 1px solid transparent;
}

QTabBar[dockFocusTabs="true"]::tab:focus,
QTabBar[dockFocusTabs="true"][focusWithin="true"]::tab:selected {
    border-bottom: 1px solid #64B5FF;
}

QDockWidget QWidget#dockFilesContents, QWidget#dockTransitionsContents, QWidget#dockEmojisContents, QWidget#dockEffectsContents, QWidget#dockCaptionContents, QWidget#dockVideoContents, QWidget#dockPropertiesContents {
    background-color: #1C1C1E;
    border-radius: 4px;
    margin-left: 16px;
    margin-right: 16px;
}

QDockWidget QWidget#dockGpuInspectorContents {
    background-color: #1C1C1E;
    border-radius: 4px;
}

QDockWidget QWidget#dockTimelineContents {
    border-radius: 0px;
    margin-left: 0px;
    margin-right: 0px;
    padding: 0px;
}

QTabBar {
    border: none;
    qproperty-drawBase: 0;
    qproperty-expanding: 0;
    qproperty-usesScrollButtons: 1;
    margin: 0px;
    padding: 0px;
}

QTabBar::tab {
    height: 16px;
    border: none;
    margin-left: 16px;
    margin-top: 16px;
    margin-bottom: 0px;
    padding-bottom: 0px;
    color: rgba(145, 195, 255, 0.4);
}

QTabWidget#exportTabs QTabBar::tab,
QTabWidget#tabCategories QTabBar::tab,
QTabWidget#tabCredits QTabBar::tab,
QTabWidget#generateTabs QTabBar::tab {
    margin-bottom: 10px;
}

/* Keep the export dialog's name/folder rows and tabs compact. */
QTabWidget#exportTabs QTabBar::tab {
    margin-top: 4px;
}

QDialog#exportDialog QPushButton#btnBrowse {
    padding-top: 2px;
    padding-bottom: 2px;
}

QTabWidget#generateTabs QTabBar::tab:selected {
    border-bottom: 1.2px solid #0A84FF;
}

QTabBar::tab:selected {
    color: rgba(145, 195, 255, 1.0);
}

QTabBar:focus {
    outline: none;
}

QTabBar::tab:focus {
    border-bottom: 1.2px solid #0A84FF;
}

QToolBox::tab:focus {
    border-left: 1.2px solid #0A84FF;
}

QCheckBox:focus {
    background-color: #3A3A3C;
}

QLineEdit#filesFilter, QLineEdit#effectsFilter, QLineEdit#transitionsFilter, QLineEdit#emojisFilter, QLineEdit#txtPropertyFilter {
    background-color: #2C2C2E;
    border-radius: 4px;
    padding: 6px;
    padding-left: 8px;
    padding-right: 8px;
}

QLineEdit,
QSpinBox,
QDoubleSpinBox {
    background-color: #121212;
    border: 1.2px solid transparent;
    border-radius: 4px;
    padding-top: 1px;
    padding-bottom: 1px;
    padding-left: 6px;
    min-height: 18px;
}

QSpinBox,
QDoubleSpinBox {
    padding-right: 22px;
}

QDoubleSpinBox#colorGradeSpinBox {
    padding-right: 14px;
}

QSpinBox::up-button,
QDoubleSpinBox::up-button,
QSpinBox::down-button,
QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    width: 16px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    margin-right: 2px;
}

QSpinBox::up-button,
QDoubleSpinBox::up-button {
    subcontrol-position: top right;
    margin-top: 1px;
    margin-bottom: 0px;
    min-height: 7px;
}

QSpinBox::down-button,
QDoubleSpinBox::down-button {
    subcontrol-position: bottom right;
    margin-top: 0px;
    margin-bottom: 1px;
    min-height: 7px;
}

QSpinBox::up-button:hover,
QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover,
QDoubleSpinBox::down-button:hover {
    background-color: rgba(145, 195, 255, 0.08);
    border-color: rgba(145, 195, 255, 0.25);
}

QSpinBox::up-button:pressed,
QDoubleSpinBox::up-button:pressed,
QSpinBox::down-button:pressed,
QDoubleSpinBox::down-button:pressed {
    background-color: rgba(145, 195, 255, 0.14);
    border-color: rgba(145, 195, 255, 0.4);
}

QSpinBox::up-arrow,
QDoubleSpinBox::up-arrow {
    image: url({PATH}themes/studio/images/spin-up-arrow.svg);
    width: 12px;
    height: 12px;
}

QSpinBox::down-arrow,
QDoubleSpinBox::down-arrow {
    image: url({PATH}themes/studio/images/spin-down-arrow.svg);
    width: 12px;
    height: 12px;
}

QLineEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border-width: 1.2px;
    border-style: solid;
    border-color: #0A84FF;
}

QLineEdit#filesFilter:focus, QLineEdit#effectsFilter:focus, QLineEdit#transitionsFilter:focus, QLineEdit#emojisFilter:focus, QLineEdit#txtPropertyFilter:focus {
    border-width: 1.2px;
    border-style: solid;
    border-color: #0A84FF;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
}

QScrollBar::handle:vertical {
    background: rgba(145, 195, 255, 51);
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    border: none;
    background: transparent;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
}

QScrollBar::handle:horizontal {
    background: rgba(145, 195, 255, 51);
    border-radius: 4px;
    min-width: 20px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
    border: none;
    background: transparent;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}

QComboBox, QDockWidget QComboBox {
    background-color: #121212;
    color: #FFFFFF;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 6px;
    padding-left: 8px;
    padding-right: 8px;
    combobox-popup: 0;
}

QComboBox:focus, QDockWidget QComboBox:focus {
    border: 1px solid #64B5FF;
    outline: none;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 40px;
    border: none;
}

QComboBox::down-arrow {
    image: url({PATH}themes/studio/images/dropdown-arrow.svg);
}

QComboBox QAbstractItemView {
    color: #FFFFFF;
    border: 1.2px solid #0A84FF;
    border-radius: 3px 3px 0px 0px;
    padding: 6px;
    padding-left: 8px;
    padding-right: 8px;
    background-color: #1C1C1E;
    text-align: left;
}

QComboBox::item {
    height: 24px;
}

QComboBox::item:selected {
    border: none;
    text-align: left;
    background-color: #2C2C2E;
}

QComboBox::item:checked {
    font-weight: bold;
    background-color: #2C2C2E;
}

QComboBox::indicator::checked {
    image: url({PATH}themes/studio/images/dropdown-tick.svg);
}

QHeaderView::section {
    background-color: #1C1C1E;
    color: #EBEBF5;
    padding: 4px;
    border: none;
}

QTableView {
    background-color: #1C1C1E;
    gridline-color: #1C1C1E;
}

QTableView#propertyTableView::item:selected {
    background-color: #2C2C2E;
    border: 1.2px solid #0A84FF;
}

QTreeView {
    background-color: #1C1C1E;
}

QListView {
    background-color: #1C1C1E;
}

QWidget#Details, QWidget#Output {
    background-color: #1C1C1E;
}

QWidget#Output QTextEdit {
    color: #EBEBF5;
}

QToolBox::tab {
    color: #EBEBF5;
    border-top: 1px solid rgba(145, 195, 255, .2);
}

QTabWidget QWidget#pageAdvancedOptions, QWidget#pageProfile, QWidget#pageImageSequenceSettings, QWidget#pageVideoSettings, QWidget#pageAudioSettings {
    background-color: #1C1C1E;
}

QTabWidget QWidget#pageVideoDetails, QWidget#pageVideoFormat, QWidget#pageAudioFormat, QWidget#pageFrameSettings {
    background-color: #1C1C1E;
}

QDialog#generateDialog QTabWidget#generateTabs::pane {
    border: none;
    background-color: #1C1C1E;
}

QDialog#generateDialog QTabWidget#generateTabs QWidget#pagePrompt,
QDialog#generateDialog QTabWidget#generateTabs QWidget#pagePoints,
QDialog#generateDialog QTabWidget#generateTabs QWidget#pageHighlight {
    background-color: #1C1C1E;
    border: none;
}

QDialog#generateDialog QLineEdit,
QDialog#generateDialog QTextEdit,
QDialog#generateDialog QComboBox {
    background-color: #1C1C1E;
    color: #EBEBF5;
    border: 1.2px solid transparent;
    border-radius: 4px;
    padding: 6px 8px;
}

QDialog#generateDialog QLineEdit:focus,
QDialog#generateDialog QTextEdit:focus,
QDialog#generateDialog QComboBox:focus {
    border: 1.2px solid #0A84FF;
}

QLineEdit:disabled,
QTextEdit:disabled,
QComboBox:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled {
    color: #808080;
}

QComboBox:disabled::drop-down {
    opacity: 0.75;
}

QWidget#cutting QPushButton#btnStart,QPushButton#btnEnd  {
    border: 1px solid #0077ED;
}

QWidget#cutting QPushButton#btnStart:disabled,QPushButton#btnEnd:disabled {
    color: #666666;
    border: 1px solid #666666;
}

QWidget#cutting QPushButton#btnAddClip {
    background-color: #0077ED;
    color: #FFFFFF;
}

QWidget#cutting QPushButton#btnAddClip:disabled,
QDialog#sourcePreviewDialog QPushButton[dialogRole="primary"]:disabled {
    background-color: #3A3A3C;
    color: #666666;
}

.property_value {
    foreground-color: #0A84FF;
    background-color: #3A3A3C;
}

.zoom_slider_playhead {
    background-color: #FABE0A;
}

QWidget#videoPreview {
    background-color: #1C1C1E;
}
        """
        path_unix_slashes = PATH.replace("\\", "/")
        self.style_sheet = f"""
QMessageBox {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #2C2C2E,
        stop: 0.55 #2C2C2E,
        stop: 1 #1C1C1E
    );
    border: 1px solid #545456;
}}
QMessageBox QLabel#qt_msgbox_label {{
    color: #F5F5F7;
    font-size: 12px;
}}
QMessageBox QPushButton[dialogRole="primary"] {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #0A84FF,
        stop: 1 #0077ED
    );
    color: #FFFFFF;
    border: 1px solid #409CFF;
}}
QMessageBox QPushButton[dialogRole="primary"]:hover {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #409CFF,
        stop: 1 #0A84FF
    );
}}
QMessageBox QPushButton[dialogRole="secondary"] {{
    color: #EBEBF5;
    background-color: #3A3A3C;
    border: 1px solid #545456;
}}
QMessageBox QPushButton[dialogRole="secondary"]:hover {{
    background-color: #48484A;
    border-color: #636366;
}}
QMessageBox QPushButton[dialogRole="cancel"] {{
    color: #AEAEB2;
}}
QMessageBox QPushButton[dialogRole="cancel"]:hover {{
    color: #EBEBF5;
    background-color: #3A3A3C;
}}
QMessageBox QPushButton[dialogRole="destructive"] {{
    color: #ffffff;
    background-color: #c43d4b;
    border: 1px solid #df5361;
}}
        """ + self.style_sheet.replace("{PATH}", f"{path_unix_slashes}/")

    def apply_theme(self):
        super().apply_theme()

        from classes.app import get_app
        from classes import ui_util
        from classes.logger import log
        from qt_api import QStyleFactory
        from qt_api import QFont

        _ = get_app()._tr

        log.info("Setting Studio Dark Fusion palette")
        self.app.setStyle(QStyleFactory.create("Fusion"))
        dark_palette = ui_util.make_dark_palette(self.app.palette())
        self.app.setPalette(dark_palette)

        # System UI font (SF Pro / .AppleSystemUIFont on macOS)
        font = QFont(".AppleSystemUIFont")
        if not font.exactMatch():
            font = QFont()
        font.setPointSizeF(11)
        self.app.setFont(font)

        # Move tabs to top (all dock areas, since restoreState() does not persist tab positions)
        for area in (Qt.TopDockWidgetArea, Qt.BottomDockWidgetArea,
                     Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea):
            self.app.window.setTabPosition(area, QTabWidget.North)

        # Tighter dock padding than Cosmic
        self.set_dock_margins([12, 0, 12, 0])
        self.set_dock_margins([0, 0, 0, 0], [0, 8, 0, 0], "dockTimelineContents")

        # Apply new stylesheet
        self.app.setStyleSheet(self.compose_stylesheet())

        # Create a transparent spacer widget
        spacer = QWidget(self.app.window)
        spacer.setFixedSize(15, 1)
        spacer.setStyleSheet("background: transparent;")

        # Main toolbar buttons
        toolbar_buttons = [
            {"action": self.app.window.actionNew, "icon": "themes/studio/images/tool-new-project.svg", "style": Qt.ToolButtonTextBesideIcon},
            {"action": self.app.window.actionOpen, "icon": "themes/studio/images/tool-open-project.svg", "style": Qt.ToolButtonTextBesideIcon},
            {"action": self.app.window.actionImportFiles, "icon": "themes/studio/images/tool-import-files.svg", "style": Qt.ToolButtonTextBesideIcon},
            {"action": self.app.window.actionProfile, "icon": "themes/studio/images/tool-profile.svg", "style": Qt.ToolButtonTextBesideIcon},
            {"expand": True},
            {"action": self.app.window.actionSave, "icon": "themes/studio/images/tool-save-project.svg", "style": Qt.ToolButtonTextBesideIcon},
            {"action": self.app.window.actionExportVideo, "icon": "themes/studio/images/tool-export.svg",
             "style": Qt.ToolButtonTextBesideIcon, "stylesheet": "QToolButton { background-color: #0A84FF; color: #FFFFFF; border: 1px solid transparent; } QToolButton:hover { background-color: #409CFF; } QToolButton:focus { background-color: #409CFF; border: 1px solid #64B5FF; } QToolButton:pressed { background-color: #64B5FF; }"},
        ]
        self.set_toolbar_buttons(self.app.window.toolBar, icon_size=20, settings=toolbar_buttons)

        self.app.window.actionColor_Grade_View.setIcon(
            QIcon(os.path.join(PATH, "themes/studio/images/view-color.svg"))
        )

        # Timeline toolbar buttons
        timeline_buttons = [
            {"action": self.app.window.actionAddTrack, "icon": "themes/studio/images/tool-add-track.svg", "style": Qt.ToolButtonTextBesideIcon, "stylesheet": "QToolButton { margin-left: 15px; }"},
            {"action": self.app.window.actionUndo, "icon": "themes/studio/images/tool-undo.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-right: 0px; border-bottom-right-radius: 0px; border-top-right-radius: 0px; }"},
            {"action": self.app.window.actionRedo, "icon": "themes/studio/images/tool-redo.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-left: 0px; border-bottom-left-radius: 0px; border-top-left-radius: 0px; }"},
            {"action": self.app.window.actionSnappingTool, "icon": "themes/studio/images/tool-snapping.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-right: 0px; border-bottom-right-radius: 0px; border-top-right-radius: 0px; }"},
            {"action": self.app.window.actionAutoKeyframes, "icon": "themes/studio/images/tool-auto-keyframes.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-left: 0px; margin-right: 0px; border-bottom-left-radius: 0px; border-top-left-radius: 0px; border-bottom-right-radius: 0px; border-top-right-radius: 0px; }"},
            {"action": self.app.window.actionTimingTool, "icon": "themes/studio/images/tool-timing.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-left: 0px; margin-right: 0px; border-bottom-left-radius: 0px; border-top-left-radius: 0px; border-bottom-right-radius: 0px; border-top-right-radius: 0px; }"},
            {"action": self.app.window.actionRazorTool, "icon": "themes/studio/images/tool-razor.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-left: 0px; margin-right: 0px; border-bottom-left-radius: 0px; border-top-left-radius: 0px; border-bottom-right-radius: 0px; border-top-right-radius: 0px; }"},
            {"action": self.app.window.actionDirectText, "icon": "images/tool-text.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-left: 0px; border-bottom-left-radius: 0px; border-top-left-radius: 0px; }"},
            {"action": self.app.window.actionAddMarker, "icon": "themes/studio/images/tool-add-marker.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-right: 0px; border-bottom-right-radius: 0px; border-top-right-radius: 0px; }"},
            {"action": self.app.window.actionPreviousMarker, "icon": "themes/studio/images/tool-prev-marker.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-left: 0px; border-bottom-left-radius: 0px; border-top-left-radius: 0px; margin-right: 0px; border-bottom-right-radius: 0px; border-top-right-radius: 0px; }"},
            {"action": self.app.window.actionNextMarker, "icon": "themes/studio/images/tool-next-marker.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QToolButton { margin-left: 0px; border-bottom-left-radius: 0px; border-top-left-radius: 0px; }"},
            {"action": self.app.window.actionCenterOnPlayhead, "icon": "themes/studio/images/tool-center-playhead.svg", "style": Qt.ToolButtonIconOnly, "stylesheet": "QWidget { margin-right: 10px; }"},
            {"widget": self.app.window.sliderZoomWidget},
            {"widget": spacer}
        ]
        self.set_toolbar_buttons(self.app.window.timelineToolbar, icon_size=12, settings=timeline_buttons)

        # Video toolbar
        toolbar_buttons = [
            {"expand": True},
            {"action": self.app.window.actionJumpStart, "icon": "themes/studio/images/tool-media-skip-back.svg", "style": Qt.ToolButtonIconOnly},
            {"action": self.app.window.actionRewind, "icon": "themes/studio/images/tool-media-rewind.svg", "style": Qt.ToolButtonIconOnly},
            {"action": self.app.window.actionPlay, "icon": "themes/studio/images/tool-media-play.svg", "style": Qt.ToolButtonIconOnly},
            {"action": self.app.window.actionFastForward, "icon": "themes/studio/images/tool-media-forward.svg", "style": Qt.ToolButtonIconOnly},
            {"action": self.app.window.actionJumpEnd, "icon": "themes/studio/images/tool-media-skip-forward.svg", "style": Qt.ToolButtonIconOnly},
            {"expand": True}
        ]
        if getattr(self.app.window, "audioOutputButton", None):
            toolbar_buttons.append({"widget": self.app.window.audioOutputButton})
        self.set_toolbar_buttons(self.app.window.videoToolbar, icon_size=32, settings=toolbar_buttons)

        from .styles import StudioDarkTimelineTheme
        self.app.window.timeline.apply_theme(StudioDarkTimelineTheme())

        # Emit signal
        self.app.window.ThemeChangedSignal.emit(self)

    def togglePlayIcon(self, isPlay):
        """ Toggle the play icon from play to pause and back """
        self._update_play_action_text(isPlay)
        button = self.app.window.videoToolbar.widgetForAction(self.app.window.actionPlay)
        if button:
            icon_name = "tool-media-pause.svg" if isPlay else "tool-media-play.svg"
            icon_path = os.path.join(PATH, "themes/studio/images", icon_name)
            icon = self.create_svg_icon(icon_path, self.app.window.videoToolbar.iconSize())
            button.setIcon(icon)
