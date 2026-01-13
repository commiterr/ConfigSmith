"""
Data models for ConfigSmith.

This module defines the core data structures used throughout ConfigSmith
for representing environment variables and their metadata.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class VariableCategory(str, Enum):
    """Categories for organizing environment variables."""
    DATABASE = "database"
    API = "api"
    APP = "app"
    AUTH = "auth"
    LOGGING = "logging"
    CACHE = "cache"
    FEATURE = "feature"
    OTHER = "other"


class EnvVariable(BaseModel):
    """
    Represents a discovered environment variable.
    
    This model captures all metadata about an environment variable
    discovered during code scanning, including its source location,
    type information, and documentation.
    """
    
    name: str = Field(..., description="Environment variable name (e.g., DATABASE_URL)")
    default_value: Optional[str] = Field(None, description="Default value if specified in code")
    type_hint: Optional[str] = Field(None, description="Inferred or declared type (e.g., 'string', 'int')")
    required: bool = Field(True, description="Whether the variable is required (no default)")
    source_file: str = Field("", description="File path where variable was found")
    line_number: int = Field(0, description="Line number in source file")
    description: Optional[str] = Field(None, description="Description from comments or docstrings")
    is_sensitive: bool = Field(False, description="Whether this appears to be a secret/credential")
    category: VariableCategory = Field(VariableCategory.OTHER, description="Variable category for grouping")
    usage_count: int = Field(1, description="Number of times variable is used in codebase")
    
    def __hash__(self):
        """Allow using EnvVariable in sets."""
        return hash(self.name)
    
    def __eq__(self, other):
        """Compare by name for deduplication."""
        if isinstance(other, EnvVariable):
            return self.name == other.name
        return False
    
    @property
    def example_value(self) -> str:
        """Generate an appropriate example value for .env.example."""
        if self.is_sensitive:
            # Generate placeholder for sensitive values
            name_lower = self.name.lower().replace("_", "-")
            return f"your-{name_lower}-here"
        
        if self.default_value is not None:
            return self.default_value
        
        # Generate type-appropriate examples
        if self.type_hint:
            type_lower = self.type_hint.lower()
            if "int" in type_lower:
                return "0"
            elif "bool" in type_lower:
                return "false"
            elif "float" in type_lower:
                return "0.0"
        
        return ""
    
    @classmethod
    def detect_category(cls, name: str) -> VariableCategory:
        """Detect category based on variable name patterns."""
        name_upper = name.upper()
        
        if any(p in name_upper for p in ["DB_", "DATABASE_", "POSTGRES_", "MYSQL_", "MONGO_", "REDIS_"]):
            return VariableCategory.DATABASE
        elif any(p in name_upper for p in ["API_", "_API_", "ENDPOINT"]):
            return VariableCategory.API
        elif any(p in name_upper for p in ["AUTH_", "JWT_", "SESSION_", "OAUTH_"]):
            return VariableCategory.AUTH
        elif any(p in name_upper for p in ["LOG_", "LOGGING_", "DEBUG"]):
            return VariableCategory.LOGGING
        elif any(p in name_upper for p in ["CACHE_", "REDIS_", "MEMCACHE"]):
            return VariableCategory.CACHE
        elif any(p in name_upper for p in ["FEATURE_", "ENABLE_", "FLAG_"]):
            return VariableCategory.FEATURE
        elif any(p in name_upper for p in ["APP_", "PORT", "HOST", "ENV", "NODE_ENV"]):
            return VariableCategory.APP
        
        return VariableCategory.OTHER
    
    @classmethod
    def detect_sensitive(cls, name: str) -> bool:
        """Detect if variable name suggests sensitive data."""
        sensitive_patterns = [
            "KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL",
            "PRIVATE", "API_KEY", "AUTH", "PASS", "PWD"
        ]
        name_upper = name.upper()
        return any(pattern in name_upper for pattern in sensitive_patterns)


class EnvFileSection(BaseModel):
    """Represents a section in the .env.example file."""
    
    name: str = Field(..., description="Section header name")
    description: Optional[str] = Field(None, description="Section description")
    variables: List[EnvVariable] = Field(default_factory=list, description="Variables in this section")


class ScanResult(BaseModel):
    """Result of scanning a codebase for environment variables."""
    
    variables: List[EnvVariable] = Field(default_factory=list, description="Discovered variables")
    files_scanned: int = Field(0, description="Number of files scanned")
    python_files: int = Field(0, description="Number of Python files scanned")
    typescript_files: int = Field(0, description="Number of TypeScript/JS files scanned")
    errors: List[str] = Field(default_factory=list, description="Errors encountered during scanning")
    
    @property
    def total_variables(self) -> int:
        """Total number of unique variables found."""
        return len(self.variables)
    
    @property
    def required_count(self) -> int:
        """Count of required variables."""
        return sum(1 for v in self.variables if v.required)
    
    @property
    def optional_count(self) -> int:
        """Count of optional variables."""
        return sum(1 for v in self.variables if not v.required)
    
    @property
    def sensitive_count(self) -> int:
        """Count of sensitive variables."""
        return sum(1 for v in self.variables if v.is_sensitive)
