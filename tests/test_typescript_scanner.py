"""
Test TypeScript/JavaScript Scanner.

Required Test #2: Detect env vars from sample TypeScript file.
"""

import pytest
from pathlib import Path

from configsmith.scanners.typescript_scanner import TypeScriptScanner


class TestTypeScriptScanner:
    """Tests for TypeScript/JavaScript environment variable scanner."""
    
    @pytest.fixture
    def scanner(self):
        """Create a scanner instance."""
        return TypeScriptScanner()
    
    @pytest.fixture
    def sample_file(self):
        """Path to sample TypeScript fixture."""
        return str(Path(__file__).parent / "fixtures" / "sample.ts")
    
    def test_detect_env_vars_from_typescript(self, scanner, sample_file):
        """
        Required Test #2: Test detecting env vars from TypeScript file.
        
        This test verifies that the scanner correctly detects:
        - process.env.VAR_NAME pattern
        - process.env["VAR_NAME"] bracket notation
        - Destructured { VAR_NAME } = process.env
        - Default values with || operator
        """
        result = scanner.scan_file(sample_file)
        
        # Verify we found variables
        assert len(result) >= 3
        
        # Get all variable names
        var_names = {v.name for v in result}
        
        # Check expected variables are detected
        assert "DATABASE_URL" in var_names
        assert "API_KEY" in var_names
        assert "PORT" in var_names
        
        # Check PORT default value extraction (from destructuring)
        port_var = next(v for v in result if v.name == "PORT")
        assert port_var.default_value == "3000"
        
        # Check DATABASE_URL default value
        db_var = next(v for v in result if v.name == "DATABASE_URL")
        assert db_var.default_value == "postgresql://localhost/db"
        
        # Check API_KEY has no default
        api_var = next(v for v in result if v.name == "API_KEY")
        assert api_var.default_value is None
        assert api_var.required is True
    
    def test_detects_bracket_notation(self, scanner, sample_file):
        """Test that process.env["VAR"] bracket notation is detected."""
        result = scanner.scan_file(sample_file)
        
        var_names = {v.name for v in result}
        assert "SECRET_KEY" in var_names
        assert "DEBUG" in var_names
    
    def test_detects_framework_patterns(self, scanner, sample_file):
        """Test that framework-specific patterns are detected."""
        result = scanner.scan_file(sample_file)
        
        var_names = {v.name for v in result}
        
        # Next.js pattern
        assert "NEXT_PUBLIC_API_URL" in var_names
        
        # React pattern
        assert "REACT_APP_NAME" in var_names
    
    def test_detects_destructuring(self, scanner, sample_file):
        """Test that destructured process.env is detected."""
        result = scanner.scan_file(sample_file)
        
        var_names = {v.name for v in result}
        
        # From destructuring: const { PORT = '3000', NODE_ENV = 'development' } = process.env
        assert "PORT" in var_names
        assert "NODE_ENV" in var_names
        
        # Check destructured default
        node_env = next(v for v in result if v.name == "NODE_ENV")
        assert node_env.default_value == "development"
    
    def test_detects_sensitive_variables(self, scanner, sample_file):
        """Test that sensitive variables are properly flagged."""
        result = scanner.scan_file(sample_file)
        
        # API_KEY should be flagged as sensitive
        api_var = next(v for v in result if v.name == "API_KEY")
        assert api_var.is_sensitive is True
        
        # SECRET_KEY should be flagged as sensitive
        secret_var = next(v for v in result if v.name == "SECRET_KEY")
        assert secret_var.is_sensitive is True
    
    def test_handles_missing_file(self, scanner):
        """Test that missing file returns empty list."""
        result = scanner.scan_file("nonexistent_file.ts")
        assert result == []
        assert len(scanner.errors) > 0
    
    def test_scan_directory(self, scanner):
        """Test recursive directory scanning."""
        fixtures_dir = str(Path(__file__).parent / "fixtures")
        result = scanner.scan_directory(fixtures_dir)
        
        var_names = {v.name for v in result}
        assert "DATABASE_URL" in var_names
        assert "PORT" in var_names
    
    def test_type_inference(self, scanner, tmp_path):
        """Test that types are inferred from default values."""
        test_file = tmp_path / "types.ts"
        test_file.write_text('''
const port = process.env.PORT || '3000';
const debug = process.env.DEBUG || 'true';
const timeout = process.env.TIMEOUT || '30';
''', encoding='utf-8')
        
        result = scanner.scan_file(str(test_file))
        
        # PORT with numeric default
        port_var = next(v for v in result if v.name == "PORT")
        assert port_var.type_hint == "int"
        
        # DEBUG with boolean default
        debug_var = next(v for v in result if v.name == "DEBUG")
        assert debug_var.type_hint == "bool"
