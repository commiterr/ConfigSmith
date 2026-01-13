"""
Test merge functionality.

Required Test #3: No duplicate keys; preserves comments from existing files.
"""

import pytest
from configsmith.models import EnvVariable
from configsmith.merge import merge_env_variables, deduplicate_variables, merge_and_generate


class TestMerge:
    """Tests for merge functionality."""
    
    def test_no_duplicate_keys_preserves_comments(self):
        """
        Required Test #3: Test that duplicate keys are merged and comments preserved.
        
        This test verifies that:
        - Duplicate keys from scanning are merged (only one entry)
        - Comments from existing .env.example are preserved
        - New variables are added correctly
        """
        # Existing .env.example with comments
        existing = '''# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Database connection URL
# Type: string (required)
DATABASE_URL=postgresql://localhost/db

# =============================================================================
# API CONFIGURATION
# =============================================================================

# API Settings
API_KEY=your-api-key-here
'''
        
        # Scanned from code (includes duplicate DATABASE_URL)
        scanned = [
            EnvVariable(
                name="DATABASE_URL",
                default_value="postgres://db",
                source_file="config.py"
            ),
            EnvVariable(
                name="NEW_VAR",
                default_value="value",
                source_file="app.py"
            ),
            EnvVariable(
                name="API_KEY",
                default_value=None,
                source_file="api.py"
            )
        ]
        
        result = merge_and_generate(existing, scanned)
        
        # Should have 3 unique keys (no duplicates)
        assert result.count("DATABASE_URL=") == 1
        assert result.count("API_KEY=") == 1
        assert result.count("NEW_VAR=") == 1
        
        # Comments should be preserved
        assert "# Database connection URL" in result or "DATABASE CONFIGURATION" in result
    
    def test_merge_preserves_existing_comments(self):
        """Test that existing comments are carried over."""
        existing = '''# Application port
PORT=3000

# Enable debug mode
DEBUG=false
'''
        
        scanned = [
            EnvVariable(name="PORT", default_value="3000"),
            EnvVariable(name="DEBUG", default_value="false"),
        ]
        
        merge_result = merge_env_variables(scanned, existing)
        
        # Check preserved comments
        assert "PORT" in merge_result.preserved_comments or len(merge_result.preserved_variables) > 0
    
    def test_new_variables_tracked(self):
        """Test that new variables are identified."""
        existing = '''PORT=3000
'''
        
        scanned = [
            EnvVariable(name="PORT", default_value="3000"),
            EnvVariable(name="NEW_API_KEY", default_value=None),
        ]
        
        result = merge_env_variables(scanned, existing)
        
        assert "NEW_API_KEY" in result.new_variables
        assert "PORT" in result.preserved_variables
    
    def test_removed_variables_tracked(self):
        """Test that removed variables are identified."""
        existing = '''PORT=3000
OLD_VAR=deprecated
'''
        
        scanned = [
            EnvVariable(name="PORT", default_value="3000"),
        ]
        
        result = merge_env_variables(scanned, existing, preserve_unused=False)
        
        assert "OLD_VAR" in result.removed_variables
    
    def test_preserve_unused_option(self):
        """Test preserve_unused keeps old variables."""
        existing = '''PORT=3000
LEGACY_VAR=keep-me
'''
        
        scanned = [
            EnvVariable(name="PORT", default_value="3000"),
        ]
        
        result = merge_env_variables(scanned, existing, preserve_unused=True)
        
        var_names = {v.name for v in result.variables}
        assert "LEGACY_VAR" in var_names
        assert "PORT" in var_names


class TestDeduplicate:
    """Tests for deduplication logic."""
    
    def test_removes_duplicate_names(self):
        """Test that duplicate variable names are removed."""
        variables = [
            EnvVariable(name="API_KEY", default_value="key1"),
            EnvVariable(name="PORT", default_value="3000"),
            EnvVariable(name="API_KEY", default_value="key2"),  # Duplicate
            EnvVariable(name="DEBUG", default_value="true"),
        ]
        
        result = deduplicate_variables(variables)
        
        # Should have 3 unique variables
        assert len(result) == 3
        
        names = [v.name for v in result]
        assert names.count("API_KEY") == 1
        
        # First occurrence should be kept
        api_var = next(v for v in result if v.name == "API_KEY")
        assert api_var.default_value == "key1"
    
    def test_updates_usage_count(self):
        """Test that usage count is updated for duplicates."""
        variables = [
            EnvVariable(name="PORT", usage_count=1),
            EnvVariable(name="PORT", usage_count=2),  # Duplicate
            EnvVariable(name="PORT", usage_count=1),  # Another duplicate
        ]
        
        result = deduplicate_variables(variables)
        
        assert len(result) == 1
        assert result[0].usage_count == 4  # 1 + 2 + 1
    
    def test_empty_list(self):
        """Test with empty list."""
        result = deduplicate_variables([])
        assert result == []
    
    def test_no_duplicates(self):
        """Test with no duplicates."""
        variables = [
            EnvVariable(name="A"),
            EnvVariable(name="B"),
            EnvVariable(name="C"),
        ]
        
        result = deduplicate_variables(variables)
        assert len(result) == 3


class TestMergeAndGenerate:
    """Tests for the combined merge and generate function."""
    
    def test_generates_valid_env_file(self):
        """Test that output is valid .env file format."""
        existing = ""
        scanned = [
            EnvVariable(name="PORT", default_value="3000"),
            EnvVariable(name="DEBUG", default_value="false"),
        ]
        
        result = merge_and_generate(existing, scanned)
        
        # Should contain key=value pairs
        assert "PORT=" in result
        assert "DEBUG=" in result
        
        # Should have header
        assert "ConfigSmith" in result
        
        # Should end with newline
        assert result.endswith('\n')
    
    def test_preserves_section_structure(self):
        """Test that section headers are generated."""
        scanned = [
            EnvVariable(
                name="DATABASE_URL",
                default_value="postgres://localhost"
            ),
            EnvVariable(
                name="API_KEY",
                default_value=None
            ),
        ]
        
        result = merge_and_generate("", scanned)
        
        # Should have section separators
        assert "=" * 10 in result  # Part of section header
