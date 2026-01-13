"""
Test Python AST Scanner.

Required Test #1: Detect env vars from sample Python file using AST.
"""

import pytest
from pathlib import Path

from configsmith.scanners.python_scanner import PythonScanner


class TestPythonScanner:
    """Tests for Python environment variable scanner."""
    
    @pytest.fixture
    def scanner(self):
        """Create a scanner instance."""
        return PythonScanner()
    
    @pytest.fixture
    def sample_file(self):
        """Path to sample Python fixture."""
        return str(Path(__file__).parent / "fixtures" / "sample.py")
    
    def test_detect_env_vars_from_python_ast(self, scanner, sample_file):
        """
        Required Test #1: Test detecting env vars from Python file using AST.
        
        This test verifies that the scanner correctly detects:
        - os.getenv() calls with and without defaults
        - os.environ.get() calls
        - os.environ[] subscript access
        - Type conversions (int(), etc.)
        """
        result = scanner.scan_file(sample_file)
        
        # Should find all environment variables
        var_names = {v.name for v in result}
        
        # Verify expected variables are found
        assert "DATABASE_URL" in var_names
        assert "API_KEY" in var_names
        assert "DEBUG" in var_names
        assert "PORT" in var_names
        assert "SECRET_KEY" in var_names
        
        # Check DATABASE_URL has correct default
        db_var = next(v for v in result if v.name == "DATABASE_URL")
        assert db_var.default_value == "postgresql://localhost/db"
        assert db_var.source_file.endswith("sample.py")
        
        # Check API_KEY has no default (required)
        api_var = next(v for v in result if v.name == "API_KEY")
        assert api_var.default_value is None
        assert api_var.required is True
        
        # Check PORT has type hint detection (wrapped in int())
        port_var = next(v for v in result if v.name == "PORT")
        assert port_var.default_value == "8000"
        assert port_var.type_hint is not None
        assert "int" in port_var.type_hint.lower()
        
        # Check DEBUG has default
        debug_var = next(v for v in result if v.name == "DEBUG")
        assert debug_var.default_value == "false"
        assert debug_var.required is False
    
    def test_detects_sensitive_variables(self, scanner, sample_file):
        """Test that sensitive variables are properly flagged."""
        result = scanner.scan_file(sample_file)
        
        # API_KEY should be flagged as sensitive
        api_var = next(v for v in result if v.name == "API_KEY")
        assert api_var.is_sensitive is True
        
        # SECRET_KEY should be flagged as sensitive
        secret_var = next(v for v in result if v.name == "SECRET_KEY")
        assert secret_var.is_sensitive is True
        
        # DATABASE_URL should not be flagged
        db_var = next(v for v in result if v.name == "DATABASE_URL")
        assert db_var.is_sensitive is False
    
    def test_detects_environ_subscript(self, scanner, sample_file):
        """Test that os.environ[] subscript access is detected."""
        result = scanner.scan_file(sample_file)
        
        # SECRET_KEY uses os.environ["KEY"] pattern
        var_names = {v.name for v in result}
        assert "SECRET_KEY" in var_names
        
        secret_var = next(v for v in result if v.name == "SECRET_KEY")
        # Subscript access has no default
        assert secret_var.default_value is None
        assert secret_var.required is True
    
    def test_handles_missing_file(self, scanner):
        """Test that missing file returns empty list and logs error."""
        result = scanner.scan_file("nonexistent_file.py")
        assert result == []
        assert len(scanner.errors) > 0
    
    def test_handles_syntax_error(self, scanner, tmp_path):
        """Test that syntax errors are handled gracefully."""
        bad_file = tmp_path / "bad_syntax.py"
        bad_file.write_text("def broken(:\n  pass", encoding='utf-8')
        
        result = scanner.scan_file(str(bad_file))
        assert result == []
        assert len(scanner.errors) > 0
    
    def test_scan_directory(self, scanner):
        """Test recursive directory scanning."""
        fixtures_dir = str(Path(__file__).parent / "fixtures")
        result = scanner.scan_directory(fixtures_dir)
        
        # Should find variables from sample.py
        var_names = {v.name for v in result}
        assert "DATABASE_URL" in var_names
        assert "API_KEY" in var_names
    
    def test_no_duplicates_in_single_file(self, scanner, tmp_path):
        """Test that duplicate variable names in same file are deduplicated."""
        test_file = tmp_path / "dupes.py"
        test_file.write_text('''
import os

# Used twice
DB_URL = os.getenv("DB_URL", "default1")
OTHER = os.getenv("DB_URL", "default2")  # Same var, different default
''', encoding='utf-8')
        
        result = scanner.scan_file(str(test_file))
        
        # Should only have one DB_URL
        db_vars = [v for v in result if v.name == "DB_URL"]
        assert len(db_vars) == 1
        
        # First occurrence wins
        assert db_vars[0].default_value == "default1"
