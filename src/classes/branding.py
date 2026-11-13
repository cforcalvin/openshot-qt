"""
 @file
 @brief Product name and user folder for this build (importable without Qt)

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
import re

PRODUCT_NAME = "Videoka"
USER_DIR_NAME = ".videoka"
# Videoka is based on OpenShot Video Editor; OpenShot's update checks, crash reports
# and usage metrics must not receive data from this fork.
UPSTREAM_SERVICES = False

# Translations are keyed by the original English strings, so the name is replaced after
# translation. The copyright holder (OpenShot Studios), links to and credit for the
# upstream project, and libopenshot are left unchanged.
_FULL_NAME = re.compile(r"(?<![/\w])(?<!based on )OpenShot Video Editor(?![/\w])")
_NAME = re.compile(r"(?<![/\w])(?<!based on )OpenShot(?![/\w]| Studios| on GitHub| Video Editor)")


def rebrand(text):
    """Replace the upstream product name in user-visible text with PRODUCT_NAME."""
    if not isinstance(text, str) or "OpenShot" not in text or PRODUCT_NAME == "OpenShot Video Editor":
        return text
    return _NAME.sub(PRODUCT_NAME, _FULL_NAME.sub(PRODUCT_NAME, text))
