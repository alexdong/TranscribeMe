#!/usr/bin/env python3
"""
Comprehensive validation script for TranscribeMe service.
This script validates configuration, SMS functionality, and API endpoints.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(command, description, capture_output=True):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")

    try:
        if capture_output:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=60
            )

            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(f"ERROR: {result.stderr}")

            return result.returncode == 0
        else:
            result = subprocess.run(command, shell=True, timeout=60)
            return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out: {command}")
        return False
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False


def validate_environment():
    """Validate environment setup."""
    print("🌍 ENVIRONMENT VALIDATION")
    print("=" * 60)

    checks = []

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(
            f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )
        checks.append(True)
    else:
        print(
            f"❌ Python version too old: {python_version.major}.{python_version.minor}"
        )
        checks.append(False)

    # Check uv installation
    uv_check = run_command("uv --version", "Checking uv installation")
    checks.append(uv_check)

    # Check project files
    required_files = [
        "pyproject.toml",
        "src/transcribe_me/__init__.py",
        "src/transcribe_me/main.py",
        "src/transcribe_me/config.py",
        ".env",
    ]

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ Found: {file_path}")
            checks.append(True)
        else:
            print(f"❌ Missing: {file_path}")
            checks.append(False)

    return all(checks)


def validate_dependencies():
    """Validate dependencies installation."""
    print("\n📦 DEPENDENCIES VALIDATION")
    print("=" * 60)

    # Install dependencies
    install_success = run_command("uv sync --dev", "Installing dependencies")

    if not install_success:
        return False

    # Check key dependencies
    key_deps = ["twilio", "openai", "fastapi", "pytest"]

    for dep in key_deps:
        check_cmd = f"uv run python -c 'import {dep}; print(f\"✅ {dep} imported successfully\")'"
        if not run_command(check_cmd, f"Checking {dep} import"):
            return False

    return True


def validate_configuration():
    """Validate configuration settings."""
    return run_command("make test-config", "Configuration Integration Tests")


def validate_sms_functionality():
    """Validate SMS functionality."""
    return run_command("make test-sms", "SMS Integration Tests (NZ Mobile Validation)")


def validate_api_endpoints():
    """Validate API endpoints."""
    return run_command("make test-api", "API Integration Tests (Webhooks & Endpoints)")


def validate_unit_tests():
    """Run unit tests."""
    return run_command("make test-unit", "Unit Tests")


def validate_code_quality():
    """Validate code quality."""
    print("\n🔧 CODE QUALITY VALIDATION")
    print("=" * 60)

    # Format code
    format_success = run_command("uv run black .", "Code formatting with black")

    # Check linting
    lint_success = run_command("uv run ruff check . --fix", "Code linting with ruff")

    return format_success and lint_success


def validate_server_startup():
    """Test server startup."""
    print("\n🚀 SERVER STARTUP VALIDATION")
    print("=" * 60)

    # Start server in background
    print("Starting server...")
    server_process = subprocess.Popen(
        ["uv", "run", "python", "-m", "transcribe_me.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait a bit for startup
    time.sleep(3)

    # Check if server is running
    if server_process.poll() is None:
        print("✅ Server started successfully")

        # Test health endpoint
        health_check = run_command(
            "curl -f http://localhost:8000/health", "Testing health endpoint"
        )

        # Stop server
        server_process.terminate()
        server_process.wait(timeout=5)

        return health_check
    else:
        stdout, stderr = server_process.communicate()
        print("❌ Server failed to start")
        if stderr:
            print(f"Error: {stderr.decode()}")
        return False


def main():
    """Run comprehensive validation."""
    print("🎯 TRANSCRIBEME COMPREHENSIVE VALIDATION")
    print("=" * 80)
    print("This script validates the complete TranscribeMe setup")
    print("including configuration, SMS functionality, and API endpoints.")
    print("=" * 80)

    validation_steps = [
        ("Environment Setup", validate_environment),
        ("Dependencies", validate_dependencies),
        ("Code Quality", validate_code_quality),
        ("Configuration", validate_configuration),
        ("Unit Tests", validate_unit_tests),
        ("SMS Functionality", validate_sms_functionality),
        ("API Endpoints", validate_api_endpoints),
        ("Server Startup", validate_server_startup),
    ]

    results = []

    for step_name, step_function in validation_steps:
        print(f"\n🔄 Running: {step_name}")
        try:
            success = step_function()
            results.append((step_name, success))

            if success:
                print(f"✅ {step_name}: PASSED")
            else:
                print(f"❌ {step_name}: FAILED")

        except Exception as e:
            print(f"❌ {step_name}: ERROR - {e}")
            results.append((step_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for step_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {step_name}")

    print(f"\n🎯 Overall Result: {passed}/{total} validations passed")

    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("🚀 TranscribeMe is ready for deployment!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed")
        print("🔧 Please address the failing validations before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
