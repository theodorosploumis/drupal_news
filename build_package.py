#!/usr/bin/env python3
"""
Build and publish script for drupal-news package.

Usage:
    python3 build_package.py --clean          # Clean build artifacts
    python3 build_package.py --build          # Build package
    python3 build_package.py --test           # Test local install
    python3 build_package.py --check          # Check package quality
    python3 build_package.py --test-upload    # Upload to TestPyPI
    python3 build_package.py --upload         # Upload to PyPI
    python3 build_package.py --version 1.0.0  # Bump version
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


class PackageBuilder:
    """Build and publish drupal-news package."""

    def __init__(self):
        self.root = Path(__file__).parent
        self.dist_dir = self.root / "dist"
        self.build_dir = self.root / "build"
        self.egg_info = self.root / "src" / "drupal_news.egg-info"
        self.version_file = self.root / "VERSION"

    def run_command(self, cmd, description=None):
        """Run a shell command and handle errors."""
        if description:
            print(f"\n{'='*60}")
            print(f"  {description}")
            print(f"{'='*60}")

        print(f"$ {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False

    def clean(self):
        """Clean build artifacts."""
        print("\n🧹 Cleaning build artifacts...")

        dirs_to_clean = [
            self.dist_dir,
            self.build_dir,
            self.egg_info,
            self.root / "drupal_news.egg-info",
        ]

        for dir_path in dirs_to_clean:
            if dir_path.exists():
                print(f"  Removing {dir_path}")
                shutil.rmtree(dir_path)

        # Clean __pycache__
        for pycache in self.root.rglob("__pycache__"):
            print(f"  Removing {pycache}")
            shutil.rmtree(pycache)

        # Clean .pyc files
        for pyc in self.root.rglob("*.pyc"):
            print(f"  Removing {pyc}")
            pyc.unlink()

        print("✓ Clean complete")

    def get_version(self):
        """Get current version from VERSION file."""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "0.1.0"

    def set_version(self, version):
        """Set version in VERSION file."""
        print(f"\n📝 Setting version to {version}")
        self.version_file.write_text(version + "\n")
        print(f"✓ Version updated to {version}")

    def build(self):
        """Build the package."""
        print("\n🔨 Building package...")

        # Ensure build tools are installed
        print("\n📦 Checking build dependencies...")
        if not self.run_command(
            [sys.executable, "-m", "pip", "install", "--upgrade", "build", "twine"],
            "Installing build tools"
        ):
            return False

        # Build the package
        if not self.run_command(
            [sys.executable, "-m", "build"],
            "Building source and wheel distributions"
        ):
            return False

        # List built files
        print("\n📦 Built packages:")
        if self.dist_dir.exists():
            for file in self.dist_dir.iterdir():
                size = file.stat().st_size / 1024
                print(f"  {file.name} ({size:.1f} KB)")

        print("\n✓ Build complete")
        return True

    def check(self):
        """Check package with twine."""
        print("\n🔍 Checking package quality...")

        if not self.dist_dir.exists() or not list(self.dist_dir.glob("*.tar.gz")):
            print("❌ No package found. Run --build first.")
            return False

        if not self.run_command(
            [sys.executable, "-m", "twine", "check", str(self.dist_dir / "*")],
            "Running twine check"
        ):
            return False

        print("\n✓ Package checks passed")
        return True

    def test_install(self):
        """Test local installation."""
        print("\n🧪 Testing local installation...")

        # Find the wheel file
        wheels = list(self.dist_dir.glob("*.whl"))
        if not wheels:
            print("❌ No wheel file found. Run --build first.")
            return False

        wheel_file = wheels[0]

        # Test install in a temporary venv would be ideal, but for simplicity:
        print(f"\n📦 Installing {wheel_file.name}...")
        if not self.run_command(
            [sys.executable, "-m", "pip", "install", "--force-reinstall", str(wheel_file)],
            "Installing package locally"
        ):
            return False

        # Test the CLI commands
        print("\n🧪 Testing CLI commands...")
        commands = [
            ["drupal-news", "--help"],
            ["drupal-news-scheduler", "--help"],
            ["drupal-news-email", "--help"],
        ]

        for cmd in commands:
            print(f"\n  Testing: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"  ✓ {cmd[0]} works")
                else:
                    print(f"  ⚠ {cmd[0]} returned non-zero exit code")
            except FileNotFoundError:
                print(f"  ❌ {cmd[0]} not found in PATH")
                return False
            except subprocess.TimeoutExpired:
                print(f"  ⚠ {cmd[0]} timed out")

        print("\n✓ Local installation test complete")
        return True

    def upload_test(self):
        """Upload to TestPyPI."""
        print("\n📤 Uploading to TestPyPI...")

        if not self.dist_dir.exists() or not list(self.dist_dir.glob("*.tar.gz")):
            print("❌ No package found. Run --build first.")
            return False

        print("\n⚠️  Make sure you have configured TestPyPI credentials:")
        print("   https://test.pypi.org/manage/account/token/")
        print()

        if not self.run_command(
            [
                sys.executable, "-m", "twine", "upload",
                "--repository", "testpypi",
                str(self.dist_dir / "*")
            ],
            "Uploading to TestPyPI"
        ):
            return False

        version = self.get_version()
        print(f"\n✓ Upload complete!")
        print(f"\n📦 Test installation with:")
        print(f"   pip install --index-url https://test.pypi.org/simple/ drupal-news=={version}")
        return True

    def upload_prod(self):
        """Upload to PyPI."""
        print("\n📤 Uploading to PyPI...")

        if not self.dist_dir.exists() or not list(self.dist_dir.glob("*.tar.gz")):
            print("❌ No package found. Run --build first.")
            return False

        print("\n⚠️  WARNING: This will upload to production PyPI!")
        print("⚠️  Make sure you have configured PyPI credentials:")
        print("   https://pypi.org/manage/account/token/")
        print()

        response = input("Are you sure you want to upload to PyPI? [y/N]: ")
        if response.lower() != 'y':
            print("Upload cancelled")
            return False

        if not self.run_command(
            [sys.executable, "-m", "twine", "upload", str(self.dist_dir / "*")],
            "Uploading to PyPI"
        ):
            return False

        version = self.get_version()
        print(f"\n✓ Upload complete!")
        print(f"\n📦 Install with:")
        print(f"   pip install drupal-news=={version}")
        return True

    def full_release(self):
        """Full release workflow."""
        print("\n🚀 Starting full release workflow...\n")

        steps = [
            ("Clean", self.clean),
            ("Check", self.check),
            ("Build", self.build),
            ("Check quality", self.check),
            ("Test install", self.test_install),
        ]

        for step_name, step_func in steps:
            print(f"\n{'='*60}")
            print(f"  Step: {step_name}")
            print(f"{'='*60}")
            if not step_func():
                print(f"\n❌ Release failed at step: {step_name}")
                return False

        print("\n" + "="*60)
        print("  ✅ Pre-release checks complete!")
        print("="*60)
        print("\n📦 Package is ready for upload")
        print("\nNext steps:")
        print("  1. Test upload: python3 build_package.py --test-upload")
        print("  2. Production upload: python3 build_package.py --upload")
        return True


def main():
    parser = argparse.ArgumentParser(description="Build and publish drupal-news package")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--build", action="store_true", help="Build package")
    parser.add_argument("--check", action="store_true", help="Check package quality")
    parser.add_argument("--test", action="store_true", help="Test local install")
    parser.add_argument("--test-upload", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--upload", action="store_true", help="Upload to PyPI")
    parser.add_argument("--version", type=str, help="Set version number")
    parser.add_argument("--release", action="store_true", help="Full release workflow")

    args = parser.parse_args()

    builder = PackageBuilder()

    # If no args, show help
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n📝 Quick start:")
        print("  1. Clean: python3 build_package.py --clean")
        print("  2. Build: python3 build_package.py --build")
        print("  3. Check: python3 build_package.py --check")
        print("  4. Test:  python3 build_package.py --test")
        print("  5. Upload to TestPyPI: python3 build_package.py --test-upload")
        print("  6. Upload to PyPI: python3 build_package.py --upload")
        print("\n Or run full workflow: python3 build_package.py --release")
        return 0

    # Execute requested actions
    success = True

    if args.version:
        builder.set_version(args.version)

    if args.clean:
        builder.clean()

    if args.build:
        success = builder.build() and success

    if args.check:
        success = builder.check() and success

    if args.test:
        success = builder.test_install() and success

    if args.test_upload:
        success = builder.upload_test() and success

    if args.upload:
        success = builder.upload_prod() and success

    if args.release:
        success = builder.full_release() and success

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
