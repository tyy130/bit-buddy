# Build Instructions for Bit Buddy Installer

## Prerequisites

### For Windows Build:
1. **Python 3.11+** with all dependencies installed:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Inno Setup 6.0+** (for creating the installer):
   - Download from: https://jrsoftware.org/isinfo.php
   - Install to default location

3. **Application Icon**:
   - Create `assets/buddy_icon.ico` (256x256 recommended)
   - You can use online tools like: https://www.icoconverter.com/

### For macOS Build:
1. **Python 3.11+** installed via Homebrew or python.org
2. **Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```
3. **Application Icon**:
   - Create `assets/buddy_icon.icns` using Icon Composer or `iconutil`

## Build Steps

### Windows Executable + Installer

#### Step 1: Build the Executable
```cmd
# From project root directory
pyinstaller buddy.spec
```

This creates:
- `dist/BitBuddy.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)

#### Step 2: Test the Executable
```cmd
# Test on local machine first
dist\BitBuddy.exe
```

Expected behavior:
- First run shows setup wizard
- Prompts for buddy name
- Asks for data folder location
- Generates unique personality
- Opens chat window

#### Step 3: Create Windows Installer
```cmd
# Compile the Inno Setup script
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" BitBuddyInstaller.iss
```

This creates:
- `dist/installer/BitBuddySetup-1.0.0.exe` - Full Windows installer

#### Step 4: Test Installer on Clean Machine
1. Copy `dist/installer/BitBuddySetup-1.0.0.exe` to test machine
2. Run installer
3. Follow wizard:
   - Accept license
   - Choose installation drive
   - Select AI model based on available resources
   - Install
4. Launch Bit Buddy from Start Menu or Desktop
5. Complete first-run setup

### macOS Application Bundle

#### Step 1: Build the .app Bundle
```bash
# From project root directory
pyinstaller buddy.spec
```

This creates:
- `dist/BitBuddy.app` - The application bundle

#### Step 2: Test the Application
```bash
# Test locally first
open dist/BitBuddy.app
```

#### Step 3: Create DMG Installer (Optional)
```bash
# Install create-dmg if not already installed
brew install create-dmg

# Create the DMG
create-dmg \
  --volname "Bit Buddy Installer" \
  --volicon "assets/buddy_icon.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "BitBuddy.app" 175 120 \
  --hide-extension "BitBuddy.app" \
  --app-drop-link 425 120 \
  "dist/BitBuddy-1.0.0.dmg" \
  "dist/BitBuddy.app"
```

#### Step 4: Code Signing (for distribution outside App Store)
```bash
# Sign the application
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  dist/BitBuddy.app

# Notarize with Apple
xcrun notarytool submit dist/BitBuddy-1.0.0.dmg \
  --apple-id "your.email@example.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait
```

### Linux Executable

#### Step 1: Build Binary
```bash
# From project root directory
pyinstaller buddy.spec
```

This creates:
- `dist/BitBuddy` - The standalone binary

#### Step 2: Create .deb Package (Debian/Ubuntu)
```bash
# Create package structure
mkdir -p bit-buddy-1.0.0/DEBIAN
mkdir -p bit-buddy-1.0.0/usr/bin
mkdir -p bit-buddy-1.0.0/usr/share/applications
mkdir -p bit-buddy-1.0.0/usr/share/icons/hicolor/256x256/apps

# Copy files
cp dist/BitBuddy bit-buddy-1.0.0/usr/bin/
cp assets/buddy_icon.png bit-buddy-1.0.0/usr/share/icons/hicolor/256x256/apps/

# Create control file
cat > bit-buddy-1.0.0/DEBIAN/control << EOF
Package: bit-buddy
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Bit Buddy Team <team@bitbuddy.dev>
Description: Personal AI companion for your filesystem
 Bit Buddy is a living digital companion that helps you
 navigate and understand your files with personality.
EOF

# Create .desktop file
cat > bit-buddy-1.0.0/usr/share/applications/bit-buddy.desktop << EOF
[Desktop Entry]
Type=Application
Name=Bit Buddy
Comment=Personal AI Companion
Exec=/usr/bin/BitBuddy
Icon=buddy_icon
Terminal=false
Categories=Utility;
EOF

# Build package
dpkg-deb --build bit-buddy-1.0.0
```

## Pre-Flight Checklist

Before building for distribution:

- [ ] Update version number in:
  - [ ] `BitBuddyInstaller.iss` (line 5)
  - [ ] `buddy.spec` (if versioning added)
  - [ ] `setup.py`
  - [ ] Documentation files

- [ ] Create application icons:
  - [ ] `assets/buddy_icon.ico` (Windows - 256x256)
  - [ ] `assets/buddy_icon.icns` (macOS)
  - [ ] `assets/buddy_icon.png` (Linux - 256x256)

- [ ] Test on clean machines:
  - [ ] Windows 10/11
  - [ ] macOS 12+ (Monterey or later)
  - [ ] Ubuntu 22.04 LTS

- [ ] Verify all dependencies included:
  - [ ] Run executable on machine without Python installed
  - [ ] Check model downloads work
  - [ ] Test file indexing with various document types

- [ ] Test installation flow:
  - [ ] Drive selection and space validation
  - [ ] Model recommendation logic
  - [ ] First-run setup wizard
  - [ ] Personality generation

- [ ] Security:
  - [ ] Code signing (Windows + macOS)
  - [ ] Virus scan (Windows)
  - [ ] Notarization (macOS)

## Troubleshooting

### "ModuleNotFoundError" when running built executable
- Check `hiddenimports` list in `buddy.spec`
- Add missing modules to the list
- Rebuild with `pyinstaller --clean buddy.spec`

### Executable too large (>500MB)
- Check `excludes` list in `buddy.spec`
- Remove unnecessary packages from requirements.txt
- Use UPX compression (enabled by default)

### GUI doesn't appear on Windows
- Ensure `console=False` in `buddy.spec`
- Check for errors in Windows Event Viewer
- Test with `console=True` to see error messages

### macOS "damaged and can't be opened"
- Application needs to be code signed
- Or: System Preferences → Security & Privacy → Allow app
- Or: `xattr -cr dist/BitBuddy.app` to remove quarantine

### Linux missing shared libraries
- Use `ldd dist/BitBuddy` to check dependencies
- Install missing libraries or bundle them with PyInstaller

## Distribution Channels

### Windows
- GitHub Releases (recommended for open source)
- Microsoft Store (requires signing)
- Direct download from website

### macOS
- GitHub Releases
- Mac App Store (requires Apple Developer account)
- Homebrew cask

### Linux
- GitHub Releases
- APT repository (Debian/Ubuntu)
- Snap Store
- Flatpak

## Continuous Integration

Example GitHub Actions workflow for automated builds:

```yaml
name: Build Installers

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller buddy.spec
      - run: iscc BitBuddyInstaller.iss
      - uses: actions/upload-artifact@v4
        with:
          name: windows-installer
          path: dist/installer/BitBuddySetup-*.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller buddy.spec
      - uses: actions/upload-artifact@v4
        with:
          name: macos-app
          path: dist/BitBuddy.app

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller buddy.spec
      - uses: actions/upload-artifact@v4
        with:
          name: linux-binary
          path: dist/BitBuddy
```

## Release Checklist

When releasing a new version:

1. [ ] Update CHANGELOG.md
2. [ ] Bump version in all config files
3. [ ] Tag release in git: `git tag v1.0.0`
4. [ ] Build all platform installers
5. [ ] Test each installer on clean machines
6. [ ] Create GitHub Release with notes
7. [ ] Upload installers as release assets
8. [ ] Update download links in README.md
9. [ ] Announce release (social media, mailing list)

---

**Need help?** Check the issues on GitHub or reach out to the community!
