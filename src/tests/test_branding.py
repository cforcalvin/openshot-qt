"""Product name applied to user-visible text."""

import unittest
from unittest.mock import patch

from classes import branding, info


class BrandingTests(unittest.TestCase):
    def test_rebrand_replaces_the_product_name(self):
        with patch.object(branding, "PRODUCT_NAME", "Videoka"):
            cases = {
                "OpenShot Video Editor": "Videoka",
                "Please restart OpenShot for all preferences to take effect.":
                    "Please restart Videoka for all preferences to take effect.",
                "OpenShot Project (*.osp)": "Videoka Project (*.osp)",
                # Left unchanged: copyright holder, upstream links and credit, libopenshot
                "Copyright OpenShot Studios, LLC": "Copyright OpenShot Studios, LLC",
                "OpenShot on GitHub": "OpenShot on GitHub",
                '<a href="https://github.com/OpenShot/openshot-qt">': '<a href="https://github.com/OpenShot/openshot-qt">',
                "Videoka is based on OpenShot Video Editor.": "Videoka is based on OpenShot Video Editor.",
                "Rebuild libopenshot": "Rebuild libopenshot",
            }
            for source, expected in cases.items():
                with self.subTest(source=source):
                    self.assertEqual(info.rebrand(source), expected)

    def test_rebrand_is_a_no_op_for_the_upstream_name(self):
        with patch.object(branding, "PRODUCT_NAME", "OpenShot Video Editor"):
            self.assertEqual(info.rebrand("Restart OpenShot"), "Restart OpenShot")
        self.assertIsNone(info.rebrand(None))

    def test_upstream_services_are_off(self):
        from classes import sentry, version
        self.assertFalse(info.UPSTREAM_SERVICES)
        with patch("classes.version.threading.Thread") as thread, \
             patch.object(sentry, "sdk") as sdk:
            version.get_current_Version()
            sentry.init_tracing()
        thread.assert_not_called()
        sdk.init.assert_not_called()

    def test_translated_ui_text_uses_the_product_name(self):
        from classes.app import OpenShotApp
        with patch.object(branding, "PRODUCT_NAME", "Videoka"), \
             patch("classes.app.QApplication.translate", return_value="Hide OpenShot:"):
            self.assertEqual(OpenShotApp.translate(None, "", "Hide OpenShot:"), "Hide Videoka:")


if __name__ == "__main__":
    unittest.main()
