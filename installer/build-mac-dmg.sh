#!/bin/sh

# Detect Homebrew prefix so this script works on both Apple Silicon
# (/opt/homebrew) and Intel (/usr/local) Macs without hard-coded paths.
if [ -x /opt/homebrew/bin/brew ]; then
    BREW_PREFIX="$(/opt/homebrew/bin/brew --prefix)"
elif [ -x /usr/local/bin/brew ]; then
    BREW_PREFIX="$(/usr/local/bin/brew --prefix)"
else
    BREW_PREFIX="/usr/local"
fi
PATH="${BREW_PREFIX}/bin:${BREW_PREFIX}/sbin:/opt/local/bin:/opt/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin"
MAC_NOTARIZE_PASSWORD=$1

# Signing and notarization identity (defaults are the official OpenShot Studios credentials).
# Set MAC_NOTARY_PROFILE to use credentials saved with `xcrun notarytool store-credentials`.
MAC_SIGN_IDENTITY="${MAC_SIGN_IDENTITY:-Developer ID Application: OpenShot Studios, LLC (C94ZNQ5JF3)}"
MAC_TEAM_ID="${MAC_TEAM_ID:-C94ZNQ5JF3}"
MAC_APPLE_ID="${MAC_APPLE_ID:-jonathan@openshot.org}"

# Get Version
VERSION=$(grep -E '^VERSION = "(.*)"' src/classes/info.py | awk '{print $3}' | tr -d '"')
echo "Found Version $VERSION"

# Set path to app bundle
OS_APP_NAME="Videoka.app"
OS_DMG_NAME="Videoka-$VERSION.dmg"
OS_PATH="build/$OS_APP_NAME/Contents"
echo "Fixing App Bundle ($OS_PATH)"

echo "Replacing Info.plist"
cp installer/Info.plist "$OS_PATH"
sed -e "s/VERSION/$VERSION/g" "$OS_PATH/Info.plist" > "$OS_PATH/Info.plist_version"
mv  "$OS_PATH/Info.plist_version" "$OS_PATH/Info.plist"
if [ "$(uname -m)" = "arm64" ]; then
    # Apple Silicon builds use Qt 6.8, which requires macOS 12.0
    MAC_MIN_VERSION="${MACOSX_DEPLOYMENT_TARGET:-12.0}"
    echo "Setting minimum macOS version to $MAC_MIN_VERSION (Apple Silicon)"
    plutil -replace LSMinimumSystemVersion -string "$MAC_MIN_VERSION" "$OS_PATH/Info.plist" || exit 1
fi

if [ -L "$OS_PATH/MacOS/lib" ]; then
    # cx_Freeze 7+ already keeps code in Contents/MacOS and resources in Contents/Resources
    # (MacOS/lib links to Resources/lib), and does not use the launch-mac wrapper.
    echo "cx_Freeze 7+ bundle layout detected: using openshot-qt as the bundle executable"
    plutil -replace CFBundleExecutable -string "openshot-qt" "$OS_PATH/Info.plist" || exit 1
else
echo "Symlink Non-Code Files to Resources"
mv "$OS_PATH/MacOS/lib/blender" "$OS_PATH/Resources/blender"; ln -s "../../Resources/blender" "$OS_PATH/MacOS/lib/blender";
mv "$OS_PATH/MacOS/lib/classes" "$OS_PATH/Resources/classes"; ln -s "../../Resources/classes" "$OS_PATH/MacOS/lib/classes";
mv "$OS_PATH/MacOS/lib/effects" "$OS_PATH/Resources/effects"; ln -s "../../Resources/effects" "$OS_PATH/MacOS/lib/effects";
mv "$OS_PATH/MacOS/lib/emojis" "$OS_PATH/Resources/emojis"; ln -s "../../Resources/emojis" "$OS_PATH/MacOS/lib/emojis";
mv "$OS_PATH/MacOS/lib/images" "$OS_PATH/Resources/images"; ln -s "../../Resources/images" "$OS_PATH/MacOS/lib/images";
mv "$OS_PATH/MacOS/lib/themes" "$OS_PATH/Resources/themes"; ln -s "../../Resources/themes" "$OS_PATH/MacOS/lib/themes";
mv "$OS_PATH/MacOS/lib/language" "$OS_PATH/Resources/language"; ln -s "../../Resources/language" "$OS_PATH/MacOS/lib/language";
mv "$OS_PATH/MacOS/lib/presets" "$OS_PATH/Resources/presets"; ln -s "../../Resources/presets" "$OS_PATH/MacOS/lib/presets";
mv "$OS_PATH/MacOS/lib/profiles" "$OS_PATH/Resources/profiles"; ln -s "../../Resources/profiles" "$OS_PATH/MacOS/lib/profiles";
mv "$OS_PATH/MacOS/lib/resources" "$OS_PATH/Resources/resources"; ln -s "../../Resources/resources" "$OS_PATH/MacOS/lib/resources";
mv "$OS_PATH/MacOS/lib/settings" "$OS_PATH/Resources/settings"; ln -s "../../Resources/settings" "$OS_PATH/MacOS/lib/settings";
cp "$OS_PATH/MacOS/settings/"* "$OS_PATH/Resources/settings/"; # Copy *.log files into settings
rm -r "$OS_PATH/MacOS/settings/" # remove old settings folder
mv "$OS_PATH/MacOS/lib/tests" "$OS_PATH/Resources/tests"; ln -s "../../Resources/tests" "$OS_PATH/MacOS/lib/tests";
mv "$OS_PATH/MacOS/lib/titles" "$OS_PATH/Resources/titles"; ln -s "../../Resources/titles" "$OS_PATH/MacOS/lib/titles";
mv "$OS_PATH/MacOS/lib/transitions" "$OS_PATH/Resources/transitions"; ln -s "../../Resources/transitions" "$OS_PATH/MacOS/lib/transitions";
mv "$OS_PATH/MacOS/lib/windows" "$OS_PATH/Resources/windows"; ln -s "../../Resources/windows" "$OS_PATH/MacOS/lib/windows";
mv "$OS_PATH/MacOS/qt.conf" "$OS_PATH/Resources/qt.conf"; ln -s "../Resources/qt.conf" "$OS_PATH/MacOS/qt.conf";
mv "$OS_PATH/MacOS/openshot-qt.hqx" "$OS_PATH/Resources/openshot-qt.hqx"; ln -s "../Resources/openshot-qt.hqx" "$OS_PATH/MacOS/openshot-qt.hqx";
mv "$OS_PATH/MacOS/lib/launch.py" "$OS_PATH/Resources/launch.py"; ln -s "../../Resources/launch.py" "$OS_PATH/MacOS/lib/launch.py";

echo "Symlink lib folder into Resources - needed to find lib/babl-ext at runtime"
ln -s "../MacOS/lib" "$OS_PATH/Resources/lib";
fi

echo "Fix permissions inside MacOS folder (all everyone to read and execute all the files inside this *.app bundle)"
chmod -R a+rx "$OS_PATH/"*

echo "Loop through bundled files and sign all binary files"
find "build" \( -iname '*.dylib' -o -iname '*.so' \) -exec codesign -s "$MAC_SIGN_IDENTITY" --timestamp=http://timestamp.apple.com/ts01 --entitlements "installer/openshot.entitlements" --force "{}" \;
if [ "$(uname -m)" = "arm64" ]; then
    # Python and Qt 6 libraries (framework binaries, or flattened copies such as lib/QtCore)
    # have no file extension and live outside Contents/Frameworks, so codesign --deep
    # does not reach them. Sign every remaining Mach-O file.
    echo "Sign extensionless Mach-O binaries (Python, Qt)"
    find "build/$OS_APP_NAME/Contents" -type f ! -name '*.dylib' ! -name '*.so' | while read -r binary; do
        if file -b "$binary" | grep -q "Mach-O"; then
            codesign -s "$MAC_SIGN_IDENTITY" --timestamp=http://timestamp.apple.com/ts01 --entitlements "installer/openshot.entitlements" --options runtime --force "$binary" || exit 1
        fi
    done || exit 1
fi

echo "Code Sign App Bundle (deep)"
codesign -s "$MAC_SIGN_IDENTITY" --force --deep --entitlements "installer/openshot.entitlements" --options runtime --timestamp=http://timestamp.apple.com/ts01 "build/$OS_APP_NAME"
if [ "$(uname -m)" = "arm64" ]; then
    echo "Verifying nested code signatures (strict)"
    codesign --verify --deep --strict --verbose=2 "build/$OS_APP_NAME" || exit 1
fi
echo "Verifying App Signing"
spctl -a -vv "build/$OS_APP_NAME"

echo "Building Custom DMG"
appdmg "installer/dmg-template.json" "build/$OS_DMG_NAME"

echo "Code Sign DMG"
codesign -s "$MAC_SIGN_IDENTITY" --force --entitlements "installer/openshot.entitlements" --timestamp=http://timestamp.apple.com/ts01 "build/$OS_DMG_NAME"

echo "Notarize DMG file (submit to Apple)"
# No errors uploading '/Users/jonathan/builds/7d5103a1/0/OpenShot/openshot-qt/build/test.zip'.
# RequestUUID = cc285719-823f-4f0b-8e71-2df4bbbdaf72
if [ -n "$MAC_NOTARY_PROFILE" ]; then
    notarize_output=$(xcrun notarytool submit --keychain-profile "$MAC_NOTARY_PROFILE" --wait "build/$OS_DMG_NAME")
else
    notarize_output=$(xcrun notarytool submit --apple-id "$MAC_APPLE_ID" --password "$MAC_NOTARIZE_PASSWORD" --team-id "$MAC_TEAM_ID" --wait "build/$OS_DMG_NAME")
fi
echo "$notarize_output"

echo "Parse Notarize Output and get Notarization ID & Status"
pat='.*id: (.*)\n.*status: ([^'$'\n'']*)'
[[ "$notarize_output" =~ $pat ]]
REQUEST_UUID="${BASH_REMATCH[1]}"
echo " Notarization ID: $REQUEST_UUID"
REQUEST_STATUS="${BASH_REMATCH[2]}"
echo " Notarization Status: $REQUEST_STATUS"

if [ "$REQUEST_UUID" == "" ]; then
    echo "Failed to locate Notarization ID, exiting with error."
    exit 1
fi
if [ "$REQUEST_STATUS" != "Accepted" ]; then
    echo "Failed to locate Notarization Status of Accepted, exiting with error."
    exit 1
fi

# Wait a few more seconds (otherwise the stapler can sometimes fail to find the ticket)
sleep 120

echo "Staple Notarization Ticket to DMG"
xcrun stapler staple "build/$OS_DMG_NAME"

echo "Verifying DMG Signing"
spctl -a -t open --context context:primary-signature -v "build/$OS_DMG_NAME"
