"""Methods to fix Mac OS X @rpath and Homebrew (/usr/local, /opt/homebrew) dependencies,
   and analyze the app bundle for OpenShot to find all external dependencies"""
import os
import platform
import struct
import subprocess
from subprocess import call
import re
import shutil


# Ignore non library/executable extensions
non_executables = [".py", ".svg", ".png", ".blend", ".a", ".pak", ".qm", ".pyc", ".txt",
                   ".jpg", ".zip", ".dat", ".conf", ".xml", ".h", ".ui", ".json", ".exe",
                   ".plist", ".xcprivacy"]

# Dependency paths to bundle: @rpath, and Homebrew on Intel (/usr/local) and Apple Silicon (/opt/homebrew)
relocate_dependency_paths = ["@rpath", "/usr/local", "/opt/homebrew"]

CPU_TYPE_ARM64 = 0x0100000C

# Framework binaries, such as "QtCore.framework/Versions/A/QtCore" (Qt 6 ships frameworks, not dylibs)
FRAMEWORK_BINARY = re.compile(r"([^/]+)\.framework/Versions/[^/]+/\1$")


def has_arm64_code(file_path):
    """Return True if file is a Mach-O binary (thin or universal) containing arm64 code"""
    try:
        with open(file_path, "rb") as f:
            magic = f.read(4)
            if magic == b"\xcf\xfa\xed\xfe":
                # Thin 64-bit Mach-O (little-endian header)
                return struct.unpack("<I", f.read(4))[0] == CPU_TYPE_ARM64
            if magic in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
                # Universal binary (big-endian header), followed by fat_arch or fat_arch_64 entries
                arch_size = 20 if magic == b"\xca\xfe\xba\xbe" else 32
                for _ in range(struct.unpack(">I", f.read(4))[0]):
                    if struct.unpack(">I", f.read(arch_size)[:4])[0] == CPU_TYPE_ARM64:
                        return True
    except (OSError, struct.error):
        pass
    return False


def adhoc_sign(file_path):
    """Replace the code signature of a binary with an ad-hoc signature"""
    result = subprocess.run(["codesign", "--force", "--sign", "-", file_path],  # nosec B603 - Fixed command and argument list; no shell.
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        raise RuntimeError("Failed to ad-hoc sign %s: %s" % (
            file_path, result.stdout.decode("utf-8", errors="replace").strip()))


def find_framework_binaries(PATH):
    """Map each framework binary suffix ("QtCore.framework/Versions/A/QtCore") to its bundled paths"""
    frameworks = {}
    for root, dirs, files in os.walk(PATH):
        for basename in files:
            file_path = os.path.join(root, basename)
            match = FRAMEWORK_BINARY.search(file_path)
            if match and not os.path.islink(file_path):
                frameworks.setdefault(match.group(0), []).append(file_path)
    return {suffix: sorted(paths) for suffix, paths in frameworks.items()}


def fix_rpath(PATH, relocate_frameworks=None):
    """FIX broken @rpath on Qt, PyQt, and Homebrew dependencies with no @rpath"""
    # Cleanup duplicate folder and files (that cx_freeze creates)
    duplicate_path = os.path.join(PATH, "lib", "openshot_qt")
    if os.path.exists(duplicate_path):
        shutil.rmtree(duplicate_path)

    # Apple Silicon builds use Qt 6 frameworks, which must resolve to the single bundled copy
    if relocate_frameworks is None:
        relocate_frameworks = platform.machine() == "arm64"
    frameworks = find_framework_binaries(PATH) if relocate_frameworks else {}
    for suffix, paths in frameworks.items():
        if len(paths) > 1:
            print("ERROR: Multiple bundled copies of %s: %s" % (suffix, ", ".join(paths)))

    # Find files matching patterns
    for root, dirs, files in os.walk(PATH):
       for basename in files:
           file_path = os.path.join(root, basename)
           relative_path = os.path.relpath(root, PATH)

           # Skip common file extensions (speed things up)
           if os.path.splitext(file_path)[-1] in non_executables or basename.startswith(".") or "profiles" in file_path:
               continue

           # Build exe path (relative from the app dir)
           executable_path = os.path.join("@executable_path", relative_path, basename)
           if relative_path == ".":
               executable_path = os.path.join("@executable_path", basename)

           # Change ID path of library files
           # Sometimes, the ID has an absolute path or invalid @rpath embedded in it, which breaks our frozen exe
           call(["install_name_tool", file_path, "-id", executable_path])

           # Loop through all dependencies of each library/executable
           raw_output = subprocess.Popen(["otool", "-L", file_path], stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
           for output in raw_output.split("\n")[1:-1]:
               # Dependencies are tab indented (universal binaries also list "(architecture arm64):" headers)
               if output.startswith("\t") and "is not an object file" not in output and ".o):" not in output:
                   dependency_path = output.split('\t')[1].split(' ')[0]
                   dependency_base_path, dependency_name = os.path.split(dependency_path)

                   # If @rpath or Homebrew found in dependency path, update with @executable_path instead
                   framework = FRAMEWORK_BINARY.search(dependency_path) if relocate_frameworks else None
                   if framework and any(path in dependency_path for path in relocate_dependency_paths):
                       bundled_paths = frameworks.get(framework.group(0))
                       if not bundled_paths:
                           print("ERROR: Framework not found in EXE folder: %s" % dependency_path)
                       else:
                           dependency_exe_path = os.path.join(
                               "@executable_path", os.path.relpath(bundled_paths[0], PATH))
                           call(["install_name_tool", file_path, "-change", dependency_path, dependency_exe_path])
                   elif any(path in dependency_path for path in relocate_dependency_paths):
                       dependency_exe_path = os.path.join("@executable_path", dependency_name)
                       if not os.path.exists(os.path.join(PATH, dependency_name)):
                           print("ERROR: Dependency PATH not found in EXE folder: %s" % dependency_path)
                       else:
                           call(["install_name_tool", file_path, "-change", dependency_path, dependency_exe_path])

           # install_name_tool invalidates existing code signatures, and arm64 macOS kills
           # any process which loads code with an invalid signature (so re-sign it)
           if has_arm64_code(file_path):
               adhoc_sign(file_path)


def normalize_version(version):
    """Convert "12" or "12.0.1" into a comparable 3-part tuple"""
    version_parts = tuple(int(part) for part in re.findall(r"\d+", version))
    return version_parts + (0,) * max(0, 3 - len(version_parts))


def min_supported_version():
    """Oldest supported macOS: 10.15 on Intel. Apple Silicon builds use Qt 6.8, which requires
    macOS 12.0 (override with MACOSX_DEPLOYMENT_TARGET when pinning a different Qt 6 release)."""
    if platform.machine() != "arm64":
        return (10, 15, 0)
    return normalize_version(os.getenv("MACOSX_DEPLOYMENT_TARGET") or "12.0")


def print_min_versions(PATH):
    """Print ALL MINIMUM and SDK VERSIONS for files in OpenShot build folder.
    This does not list all dependent libraries though, and sometimes one of those can cause issues."""
    # Use 2 different matches, due to different output from different libraries (depending on compiler)
    REGEX_SDK_MATCH = re.compile(r'.*(LC_VERSION_MIN_MACOSX).*version (\d+\.\d+).*sdk (\d+\.\d+).*(cmd)', re.DOTALL)
    REGEX_SDK_MATCH2 = re.compile(r'LC_BUILD_VERSION.*?minos\s+(\S+)\s+sdk\s+(\S+)', re.DOTALL)

    minimum_version = min_supported_version()

    VERSIONS = {}

    # Find files matching patterns
    for root, dirs, files in os.walk(PATH):
       for basename in files:
           file_path = os.path.join(root, basename)
           file_parts = file_path.split("/")

           # Skip common file extensions (speed things up)
           if os.path.splitext(file_path)[-1] in non_executables or basename.startswith("."):
               continue

           command = ["otool", "-l", file_path]
           if platform.machine() == "arm64" and has_arm64_code(file_path):
               # Universal binaries (e.g. cx_Freeze launchers) also contain an x86_64 slice with
               # legacy load commands, which would be misreported as the arm64 minimum version
               command = ["otool", "-arch", "arm64", "-l", file_path]
           raw_output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
           matches = REGEX_SDK_MATCH.findall(raw_output)
           matches2 = REGEX_SDK_MATCH2.findall(raw_output)
           min_version = None
           sdk_version = None
           if matches and len(matches[0]) == 4:
               min_version = matches[0][1]
               sdk_version = matches[0][2]
           elif matches2 and len(matches2[0]) == 2:
               min_version = matches2[0][0]
               sdk_version = matches2[0][1]

           if min_version and sdk_version:
               print("... scanning %s for min version (min: %s, sdk: %s)" % (file_path.replace(PATH, ""),
                                                                             min_version, sdk_version))
               # Organize by MIN version
               if min_version in VERSIONS:
                   if file_path not in VERSIONS[min_version]:
                       VERSIONS[min_version].append(file_path)
               else:
                   VERSIONS[min_version] = [file_path]

               if normalize_version(min_version) > minimum_version:
                   print("ERROR!!!! Minimum OS X version not met for %s" % file_path)

    print("\nSummary of Minimum Mac SDKs for Dependencies:")
    for key in sorted(VERSIONS.keys()):
        print("\n%s" % key)
        for file_path in VERSIONS[key]:
            print("  %s" % file_path)

    print("\nCount of Minimum Mac SDKs for Dependencies:")
    for key in sorted(VERSIONS.keys()):
        print("%s (%d)" % (key, len(VERSIONS[key])))


if __name__ == "__main__":
    # Run these methods manually for testing.
    # Usage: python3 fix_qt5_rpath.py [BUILD_PATH]
    # With no argument, use the sole cx_Freeze build directory. Require an
    # explicit path when multiple architectures or Python builds coexist.
    import sys
    import glob

    if len(sys.argv) > 1:
        PATH = sys.argv[1]
    else:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = sorted(path for path in
                            glob.glob(os.path.join(repo_root, "build", "exe.macosx-*"))
                            if os.path.isdir(path))
        if not candidates:
            sys.exit(
                "Usage: python3 fix_qt5_rpath.py [BUILD_PATH]\n"
                "No cx_Freeze build directory found under %s/build/exe.macosx-*"
                % repo_root
            )
        if len(candidates) > 1:
            sys.exit("Multiple build directories found; pass BUILD_PATH explicitly:\n%s"
                     % "\n".join(candidates))
        PATH = candidates[0]

    if not os.path.isdir(PATH):
        sys.exit("Build directory does not exist: %s" % PATH)

    print("Running fix_rpath and print_min_versions against: %s" % PATH)
    fix_rpath(PATH)
    print_min_versions(PATH)
