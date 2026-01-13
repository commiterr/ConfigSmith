"""
ConfigSmith - Automatically generate .env.example files from source code.

ConfigSmith scans your codebase for environment variable usage patterns,
extracts keys and default values, and generates documented .env.example files.
"""

__version__ = "1.0.0"
__author__ = "ConfigSmith Contributors"

from configsmith.models import EnvVariable
from configsmith.scanners.python_scanner import PythonScanner
from configsmith.scanners.typescript_scanner import TypeScriptScanner
from configsmith.generator import EnvExampleGenerator
from configsmith.merge import merge_env_variables

__all__ = [
    "EnvVariable",
    "PythonScanner",
    "TypeScriptScanner",
    "EnvExampleGenerator",
    "merge_env_variables",
]
