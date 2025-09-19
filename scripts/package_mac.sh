#!/bin/bash

# macOS packaging script for LedgerLite
# This script creates a distributable .app bundle for macOS

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📦 Packaging LedgerLite for macOS"
echo "Project root: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run dev_run.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install PyInstaller if not already installed
echo "📥 Installing PyInstaller..."
pip install pyinstaller

# Create build directory
BUILD_DIR="build"
DIST_DIR="dist"
if [ -d "$BUILD_DIR" ]; then
    echo "🧹 Cleaning build directory..."
    rm -rf "$BUILD_DIR"
fi
if [ -d "$DIST_DIR" ]; then
    echo "🧹 Cleaning dist directory..."
    rm -rf "$DIST_DIR"
fi

# Create PyInstaller spec file
echo "📝 Creating PyInstaller spec file..."
cat > ledgerlite.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ledgerlite/app/main.py'],
    pathex=['$PROJECT_ROOT'],
    binaries=[],
    datas=[
        ('ledgerlite/assets/styles.qss', 'ledgerlite/assets'),
        ('ledgerlite/assets/icons', 'ledgerlite/assets/icons'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'sqlalchemy',
        'pandas',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LedgerLite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ledgerlite/assets/icons/app_icon.icns',
)

app = BUNDLE(
    exe,
    name='LedgerLite.app',
    icon='ledgerlite/assets/icons/app_icon.icns',
    bundle_identifier='com.hexsoftware.ledgerlite',
    info_plist={
        'CFBundleName': 'LedgerLite',
        'CFBundleDisplayName': 'LedgerLite',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.hexsoftware.ledgerlite',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14',
    },
)
EOF

# Build the application
echo "🔨 Building application with PyInstaller..."
pyinstaller ledgerlite.spec

# Check if build was successful
if [ -d "$DIST_DIR/LedgerLite.app" ]; then
    echo "✅ Build successful!"
    echo "📱 Application bundle created at: $DIST_DIR/LedgerLite.app"
    
    # Get bundle size
    BUNDLE_SIZE=$(du -sh "$DIST_DIR/LedgerLite.app" | cut -f1)
    echo "📊 Bundle size: $BUNDLE_SIZE"
    
    # Create DMG (optional)
    read -p "🎁 Create DMG installer? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Creating DMG installer..."
        
        # Create DMG
        DMG_NAME="LedgerLite-1.0.0-macOS.dmg"
        hdiutil create -volname "LedgerLite" -srcfolder "$DIST_DIR/LedgerLite.app" -ov -format UDZO "$DIST_DIR/$DMG_NAME"
        
        if [ -f "$DIST_DIR/$DMG_NAME" ]; then
            DMG_SIZE=$(du -sh "$DIST_DIR/$DMG_NAME" | cut -f1)
            echo "✅ DMG created: $DIST_DIR/$DMG_NAME ($DMG_SIZE)"
        else
            echo "❌ Failed to create DMG"
        fi
    fi
    
    echo ""
    echo "🎉 Packaging complete!"
    echo "📁 Output directory: $DIST_DIR"
    echo "🚀 You can now distribute LedgerLite.app"
    
else
    echo "❌ Build failed!"
    exit 1
fi

# Clean up
echo "🧹 Cleaning up..."
rm -f ledgerlite.spec

echo "✨ Done!"
