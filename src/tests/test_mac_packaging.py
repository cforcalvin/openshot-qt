"""Mac packaging regression checks using binary fixtures and mocked Apple tools."""

import contextlib
import importlib.util
import io
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

from tests.source_tree import source_path


spec = importlib.util.spec_from_file_location(
    "fix_qt5_rpath", source_path("installer/fix_qt5_rpath.py"))
rpath = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rpath)
arch_spec = importlib.util.spec_from_file_location(
    "check_mac_arch", source_path("installer/check_mac_arch.py"))
arch = importlib.util.module_from_spec(arch_spec)
arch_spec.loader.exec_module(arch)
X86_64 = 0x01000007


def thin_binary(machine):
    return b"\xcf\xfa\xed\xfe" + struct.pack("<I", machine) + bytes(24)


class MacPackagingTests(unittest.TestCase):
    def test_arm_detection_for_thin_universal_and_invalid_files(self):
        fixtures = [(thin_binary(X86_64), False),
                    (thin_binary(rpath.CPU_TYPE_ARM64), True),
                    (b"not a Mach-O file", False),
                    (b"\xcf\xfa\xed\xfe", False)]
        for magic, arch_size in ((b"\xca\xfe\xba\xbe", 20),
                                 (b"\xca\xfe\xba\xbf", 32)):
            entries = b"".join(struct.pack(">I", machine) + bytes(arch_size - 4)
                               for machine in (X86_64, rpath.CPU_TYPE_ARM64))
            fixtures.append((magic + struct.pack(">I", 2) + entries, True))
            fixtures.append((magic + struct.pack(">I", 2), False))
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "example.dylib"
            for data, expected in fixtures:
                with self.subTest(data=data):
                    binary.write_bytes(data)
                    self.assertEqual(rpath.has_arm64_code(binary), expected)

    def test_codesign_failure_stops_packaging(self):
        result = mock.Mock(returncode=1, stdout=b"signature rejected")
        with mock.patch.object(rpath.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "signature rejected"):
                rpath.adhoc_sign("example.dylib")

    def test_intel_and_arm_dependency_relocation(self):
        for machine, prefix in ((X86_64, "/usr/local"),
                                (rpath.CPU_TYPE_ARM64, "/opt/homebrew")):
            with self.subTest(machine=machine), tempfile.TemporaryDirectory() as directory:
                binary = Path(directory) / "openshot-qt"
                binary.write_bytes(thin_binary(machine))
                dependency = Path(directory) / "libQt5Core.dylib"
                dependency.write_bytes(thin_binary(X86_64))
                source = prefix + "/lib/libQt5Core.dylib"
                output = ("openshot-qt (architecture arm64):\n"
                          "\t%s (compatibility version 5.0.0, current version 5.15.0)\n" % source)
                process = mock.Mock()
                process.communicate.return_value = (output.encode(), None)
                with mock.patch.object(rpath.subprocess, "Popen", return_value=process), \
                     mock.patch.object(rpath, "call") as install_name_tool, \
                     mock.patch.object(rpath, "adhoc_sign") as sign:
                    rpath.fix_rpath(directory)
                install_name_tool.assert_any_call([
                    "install_name_tool", str(binary), "-change", source,
                    "@executable_path/libQt5Core.dylib"])
                if machine == rpath.CPU_TYPE_ARM64:
                    sign.assert_called_once_with(str(binary))
                else:
                    sign.assert_not_called()

    def test_qt6_framework_dependencies_relocate_to_the_bundled_framework(self):
        source = "@rpath/QtCore.framework/Versions/A/QtCore"
        bundled = "lib/PyQt6/Qt6/lib/QtCore.framework/Versions/A/QtCore"
        for relocate in (True, False):
            with self.subTest(relocate=relocate), tempfile.TemporaryDirectory() as directory:
                binary = Path(directory) / "_openshot.so"
                binary.write_bytes(thin_binary(rpath.CPU_TYPE_ARM64))
                framework = Path(directory) / bundled
                framework.parent.mkdir(parents=True)
                framework.write_bytes(thin_binary(rpath.CPU_TYPE_ARM64))
                (framework.parents[2] / "QtCore").symlink_to("Versions/A/QtCore")
                process = mock.Mock()
                process.communicate.return_value = (
                    ("_openshot.so:\n\t%s (compatibility version 6.0.0, current version 6.8.2)\n"
                     % source).encode(), None)
                output = io.StringIO()
                with mock.patch.object(rpath.subprocess, "Popen", return_value=process), \
                     mock.patch.object(rpath, "call") as install_name_tool, \
                     mock.patch.object(rpath, "adhoc_sign"), \
                     contextlib.redirect_stdout(output):
                    rpath.fix_rpath(directory, relocate_frameworks=relocate)
                change = ["install_name_tool", str(binary), "-change", source,
                          "@executable_path/" + bundled]
                self.assertEqual(change in [c.args[0] for c in install_name_tool.call_args_list], relocate)
                self.assertNotIn("Multiple bundled copies", output.getvalue())

    def test_duplicate_qt6_frameworks_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            for prefix in ("lib/PyQt6/Qt6/lib", "lib"):
                framework = Path(directory) / prefix / "QtCore.framework/Versions/A/QtCore"
                framework.parent.mkdir(parents=True, exist_ok=True)
                framework.write_bytes(thin_binary(rpath.CPU_TYPE_ARM64))
            process = mock.Mock()
            process.communicate.return_value = (b"QtCore:\n", None)
            output = io.StringIO()
            with mock.patch.object(rpath.subprocess, "Popen", return_value=process), \
                 mock.patch.object(rpath, "call"), mock.patch.object(rpath, "adhoc_sign"), \
                 contextlib.redirect_stdout(output):
                rpath.fix_rpath(directory, relocate_frameworks=True)
            self.assertIn("ERROR: Multiple bundled copies of QtCore.framework", output.getvalue())

    def test_arm64_bundle_check(self):
        qtcore = "lib/PyQt6/Qt6/lib/QtCore.framework/Versions/A/QtCore"
        universal = (b"\xca\xfe\xba\xbe" + struct.pack(">I", 2) +
                     b"".join(struct.pack(">I", machine) + bytes(16)
                              for machine in (X86_64, rpath.CPU_TYPE_ARM64)))
        java_class = b"\xca\xfe\xba\xbe" + struct.pack(">I", 52)
        cases = (
            ("native", {qtcore: thin_binary(rpath.CPU_TYPE_ARM64), "openshot-qt": universal,
                        "lib/Example.class": java_class, "README.txt": b"text"}, None),
            ("intel library", {qtcore: thin_binary(rpath.CPU_TYPE_ARM64),
                               "libopenshot.dylib": thin_binary(X86_64)}, "libopenshot.dylib"),
            ("duplicate Qt", {qtcore: thin_binary(rpath.CPU_TYPE_ARM64),
                              "QtCore": thin_binary(rpath.CPU_TYPE_ARM64)}, "exactly one QtCore"),
            ("missing Qt", {"openshot-qt": universal}, "found 0"),
        )
        for name, files, error in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                for relative_path, data in files.items():
                    file_path = Path(directory) / relative_path
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_bytes(data)
                if qtcore in files:
                    (Path(directory) / qtcore).parents[2].joinpath("QtCore").symlink_to("Versions/A/QtCore")
                with contextlib.redirect_stdout(io.StringIO()):
                    if error:
                        with self.assertRaisesRegex(RuntimeError, error):
                            arch.check_bundle(directory)
                    else:
                        report = arch.check_bundle(directory)
                        self.assertEqual(report["qtcore"], qtcore)
                        self.assertEqual(report["macho_files"], 2)

    def test_minimum_versions_read_only_the_arm64_slice_on_apple_silicon(self):
        universal = (b"\xca\xfe\xba\xbe" + struct.pack(">I", 2) +
                     b"".join(struct.pack(">I", machine) + bytes(16)
                              for machine in (X86_64, rpath.CPU_TYPE_ARM64)))
        for arch, data, expected in (("arm64", universal, ["otool", "-arch", "arm64", "-l"]),
                                     ("arm64", thin_binary(X86_64), ["otool", "-l"]),
                                     ("x86_64", universal, ["otool", "-l"])):
            with self.subTest(arch=arch, expected=expected), tempfile.TemporaryDirectory() as directory:
                binary = Path(directory) / "openshot-qt"
                binary.write_bytes(data)
                process = mock.Mock()
                process.communicate.return_value = (b"cmd LC_BUILD_VERSION\n minos 11.0\n sdk 15.5\n", None)
                with mock.patch.object(rpath.platform, "machine", return_value=arch), \
                     mock.patch.object(rpath.subprocess, "Popen", return_value=process) as popen, \
                     contextlib.redirect_stdout(io.StringIO()):
                    rpath.print_min_versions(directory)
                popen.assert_called_once_with(expected + [str(binary)], stdout=rpath.subprocess.PIPE)

    def test_minimum_versions_ignore_trailing_zero_components(self):
        for arch, version, target, error in (("arm64", "11.0", None, False),
                                             ("arm64", "12.0", None, False),
                                             ("arm64", "12.0.0", None, False),
                                             ("arm64", "12.0.1", None, True),
                                             ("arm64", "13.0", "13.0", False),
                                             ("arm64", "13.0", None, True),
                                             ("x86_64", "10.15.0", None, False),
                                             ("x86_64", "10.15.0", "13.0", False),
                                             ("x86_64", "11.0", None, True)):
            with self.subTest(arch=arch, version=version, target=target), \
                 tempfile.TemporaryDirectory() as directory:
                (Path(directory) / "example.dylib").write_bytes(thin_binary(X86_64))
                process = mock.Mock()
                process.communicate.return_value = (
                    ("cmd LC_BUILD_VERSION\n minos %s\n sdk 15.0\n" % version).encode(), None)
                output = io.StringIO()
                environment = {"MACOSX_DEPLOYMENT_TARGET": target} if target else {}
                with mock.patch.object(rpath.platform, "machine", return_value=arch), \
                     mock.patch.dict(rpath.os.environ, environment, clear=True), \
                     mock.patch.object(rpath.subprocess, "Popen", return_value=process), \
                     contextlib.redirect_stdout(output):
                    rpath.print_min_versions(directory)
                self.assertEqual("ERROR!!!!" in output.getvalue(), error)
                self.assertIn("min: %s, sdk: 15.0" % version, output.getvalue())


if __name__ == "__main__":
    unittest.main()
