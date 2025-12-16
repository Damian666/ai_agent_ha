"""Test constants and basic imports that should always work."""

import os
import sys
import importlib.util


def test_constants_file_exists():
    """Test that the constants file exists and can be read."""
    const_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "custom_components",
        "lm_studio_agent",
        "const.py",
    )
    assert os.path.exists(const_path), f"Constants file not found at {const_path}"


def test_domain_is_correct():
    """Test that domain constant is correct."""
    # Import const.py directly to avoid __init__.py issues
    const_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "custom_components",
        "lm_studio_agent",
        "const.py",
    )
    const_path = os.path.abspath(const_path)

    spec = importlib.util.spec_from_file_location("const", const_path)
    const_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(const_module)

    assert hasattr(const_module, "DOMAIN")
    assert const_module.DOMAIN == "lm_studio_agent"





def test_python_version_compatibility():
    """Test that we're running on a supported Python version."""
    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version_info}"


def test_manifest_file_exists():
    """Test that manifest.json exists."""
    manifest_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "custom_components",
        "lm_studio_agent",
        "manifest.json",
    )
    assert os.path.exists(manifest_path), "Manifest file not found"
