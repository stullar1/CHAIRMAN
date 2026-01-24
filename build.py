"""
CHAIRMAN - Build Script
Builds the application for the current platform

Usage:
    python build.py          # Build executable
    python build.py --clean  # Clean and rebuild
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode == 0


def clean_build():
    """Remove previous build artifacts."""
    print("\nCleaning previous builds...")
    for folder in ['build', 'dist']:
        path = PROJECT_ROOT / folder
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed: {folder}/")


def generate_assets():
    """Generate required assets (sounds, icons)."""
    # Generate sounds
    sounds_script = PROJECT_ROOT / 'assets' / 'sounds' / 'generate_sounds.py'
    if sounds_script.exists():
        if not (PROJECT_ROOT / 'assets' / 'sounds' / 'click.wav').exists():
            run_command([sys.executable, str(sounds_script)], "Generating sound files")

    # Generate icons
    icons_script = PROJECT_ROOT / 'assets' / 'icons' / 'generate_icons.py'
    if icons_script.exists():
        if not (PROJECT_ROOT / 'assets' / 'icons' / 'app_icon.ico').exists():
            run_command([sys.executable, str(icons_script)], "Generating app icons")


def build_executable():
    """Build the executable using PyInstaller."""
    system = platform.system().lower()

    if system == 'darwin':
        spec_file = 'chairman_macos.spec'
    else:
        spec_file = 'chairman.spec'

    return run_command(
        ['pyinstaller', spec_file, '--clean', '-y'],
        f"Building {system.title()} executable"
    )


def build_installer_windows():
    """Build Windows installer using Inno Setup (Windows only)."""
    if platform.system().lower() != 'windows':
        print("Skipping Windows installer (not on Windows)")
        return True

    # Check for Inno Setup
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    inno_exe = None
    for path in inno_paths:
        if os.path.exists(path):
            inno_exe = path
            break

    if not inno_exe:
        print("\nInno Setup not found. Skipping installer creation.")
        print("Install from: https://jrsoftware.org/isinfo.php")
        return True

    iss_file = PROJECT_ROOT / 'installer' / 'windows' / 'chairman_setup.iss'
    return run_command(
        [inno_exe, str(iss_file)],
        "Building Windows installer"
    )


def main():
    """Main build process."""
    print(f"""
    ============================================================
                    CHAIRMAN - Build Script

      Platform: {platform.system()}
    ============================================================
    """)

    # Parse arguments
    clean = '--clean' in sys.argv

    if clean:
        clean_build()

    # Generate assets
    generate_assets()

    # Build executable
    if not build_executable():
        print("\n[ERROR] Build failed!")
        return 1

    # Build installer (Windows only)
    if platform.system().lower() == 'windows':
        build_installer_windows()

    # Print results
    print(f"""
    ============================================================
                       Build Complete!
    ============================================================

    Output location:
      - Executable: dist/CHAIRMAN/
    """)

    if platform.system().lower() == 'windows':
        installer_dir = PROJECT_ROOT / 'installer' / 'windows' / 'Output'
        if installer_dir.exists():
            print(f"      - Installer:  {installer_dir}/")

    return 0


if __name__ == '__main__':
    sys.exit(main())
