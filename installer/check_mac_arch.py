#!/usr/bin/env python3
"""Check a frozen macOS app for native Apple Silicon (arm64) code.

Fails when any Mach-O file in the bundle lacks an arm64 slice (it could only load
under Rosetta), or when more than one QtCore binary is bundled (libopenshot and the
Qt binding must share a single Qt)."""
import argparse
import json
import os
from pathlib import Path
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_qt5_rpath import has_arm64_code  # noqa: E402

THIN_MAGICS = (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xfe\xed\xfa\xce")
FAT_MAGICS = (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf")
QTCORE_BINARY = re.compile(r"^(QtCore|libQt[56]Core(\.\d+)*\.dylib)$")


def is_macho(file_path):
    """Return True for thin or universal Mach-O files"""
    try:
        with open(file_path, "rb") as f:
            magic = f.read(4)
            if magic in THIN_MAGICS:
                return True
            if magic in FAT_MAGICS:
                # Java class files share the 0xcafebabe magic, but store a version (>= 45) here
                return 0 < struct.unpack(">I", f.read(4))[0] < 32
    except (OSError, struct.error):
        pass
    return False


def check_bundle(bundle):
    bundle = Path(bundle).resolve()
    if not bundle.is_dir():
        raise RuntimeError("Bundle not found: %s" % bundle)
    binaries = []
    missing_arm64 = []
    qtcore = []
    for root, dirs, files in os.walk(bundle):
        for basename in files:
            file_path = os.path.join(root, basename)
            if os.path.islink(file_path) or not is_macho(file_path):
                continue
            relative_path = os.path.relpath(file_path, bundle)
            binaries.append(relative_path)
            if not has_arm64_code(file_path):
                missing_arm64.append(relative_path)
            if QTCORE_BINARY.match(basename):
                qtcore.append(relative_path)
    problems = []
    if not binaries:
        problems.append("No Mach-O files found in %s" % bundle)
    if missing_arm64:
        problems.append("Mach-O files without arm64 code:\n  " + "\n  ".join(sorted(missing_arm64)))
    if len(qtcore) != 1:
        problems.append("Expected exactly one QtCore binary, found %d:\n  %s"
                        % (len(qtcore), "\n  ".join(sorted(qtcore))))
    if problems:
        raise RuntimeError("\n".join(problems))
    report = {"bundle": str(bundle), "architecture": "arm64",
              "macho_files": len(binaries), "qtcore": qtcore[0]}
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", help="Path to the .app bundle (or its Contents/MacOS folder)")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = check_bundle(args.bundle)
    except RuntimeError as ex:
        sys.exit("ERROR: %s" % ex)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
