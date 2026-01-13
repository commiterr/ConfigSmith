"""
Python AST-based scanner for environment variable detection.

This module uses Python's Abstract Syntax Tree (AST) to parse Python source
files and detect environment variable usage patterns such as os.getenv(),
os.environ.get(), and os.environ[] access.
"""

import ast
import os
from pathlib import Path
from typing import List, Optional, Set, Dict, Any
from configsmith.models import EnvVariable, VariableCategory


class PythonEnvVisitor(ast.NodeVisitor):
    """
    AST visitor that detects environment variable usage in Python code.
    
    Detects the following patterns:
    - os.getenv("VAR_NAME", "default")
    - os.environ.get("VAR_NAME", "default")
    - os.environ["VAR_NAME"]
    - Environment variables in f-strings
    """
    
    def __init__(self, source_file: str, source_code: str):
        self.source_file = source_file
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.env_vars: List[EnvVariable] = []
        self.seen: Set[str] = set()
        self._current_function: Optional[str] = None
        self._docstrings: Dict[str, str] = {}
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track current function for context and extract docstrings."""
        self._current_function = node.name
        
        # Extract docstring
        if (node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            self._docstrings[node.name] = node.body[0].value.value
        
        self.generic_visit(node)
        self._current_function = None
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Track async functions the same way."""
        self._current_function = node.name
        self.generic_visit(node)
        self._current_function = None
    
    def visit_Call(self, node: ast.Call):
        """Visit function calls to detect os.getenv, os.environ.get, etc."""
        
        # Detect os.getenv("VAR_NAME", "default")
        if self._is_getenv_call(node):
            self._extract_getenv(node)
        
        # Detect os.environ.get("VAR_NAME", "default")
        elif self._is_environ_get(node):
            self._extract_environ_get(node)
        
        # Detect dotenv pattern
        elif self._is_dotenv_call(node):
            pass  # Just note that dotenv is used
        
        self.generic_visit(node)
    
    def visit_Subscript(self, node: ast.Subscript):
        """Visit subscript to detect os.environ["VAR_NAME"]."""
        
        if self._is_environ_subscript(node):
            self._extract_environ_subscript(node)
        
        self.generic_visit(node)
    
    def _is_getenv_call(self, node: ast.Call) -> bool:
        """Check if call is os.getenv()."""
        return (
            isinstance(node.func, ast.Attribute) and
            node.func.attr == "getenv" and
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == "os"
        )
    
    def _is_environ_get(self, node: ast.Call) -> bool:
        """Check if call is os.environ.get()."""
        if not isinstance(node.func, ast.Attribute):
            return False
        if node.func.attr != "get":
            return False
        
        # Check for os.environ.get
        value = node.func.value
        if isinstance(value, ast.Attribute):
            if value.attr == "environ" and isinstance(value.value, ast.Name):
                return value.value.id == "os"
        
        return False
    
    def _is_dotenv_call(self, node: ast.Call) -> bool:
        """Check if this is a dotenv.load_dotenv() call."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "load_dotenv"
        if isinstance(node.func, ast.Name):
            return node.func.id == "load_dotenv"
        return False
    
    def _is_environ_subscript(self, node: ast.Subscript) -> bool:
        """Check if subscript is os.environ[...]."""
        if not isinstance(node.value, ast.Attribute):
            return False
        if node.value.attr != "environ":
            return False
        if not isinstance(node.value.value, ast.Name):
            return False
        return node.value.value.id == "os"
    
    def _extract_getenv(self, node: ast.Call):
        """Extract env var from os.getenv() call."""
        if not node.args:
            return
        
        # Get variable name (first argument)
        var_name = self._get_string_value(node.args[0])
        if not var_name:
            return  # Dynamic key, skip
        
        # Get default value (second argument if exists)
        default = None
        if len(node.args) > 1:
            default = self._get_string_value(node.args[1])
        
        # Check for keyword argument 'default'
        for keyword in node.keywords:
            if keyword.arg == "default":
                default = self._get_string_value(keyword.value)
        
        # Detect type from wrapping function (e.g., int(os.getenv(...)))
        type_hint = self._detect_type_wrapper(node)
        
        self._add_env_var(
            name=var_name,
            default_value=default,
            line_number=node.lineno,
            type_hint=type_hint
        )
    
    def _extract_environ_get(self, node: ast.Call):
        """Extract env var from os.environ.get() call."""
        if not node.args:
            return
        
        var_name = self._get_string_value(node.args[0])
        if not var_name:
            return
        
        default = None
        if len(node.args) > 1:
            default = self._get_string_value(node.args[1])
        
        self._add_env_var(
            name=var_name,
            default_value=default,
            line_number=node.lineno
        )
    
    def _extract_environ_subscript(self, node: ast.Subscript):
        """Extract env var from os.environ["VAR"] access."""
        var_name = self._get_string_value(node.slice)
        if var_name:
            self._add_env_var(
                name=var_name,
                default_value=None,
                line_number=node.lineno
            )
    
    def _get_string_value(self, node: ast.AST) -> Optional[str]:
        """Extract string value from an AST node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        # For Python 3.7 compatibility (ast.Str is deprecated but still exists)
        if hasattr(ast, 'Str') and isinstance(node, ast.Str):
            return node.s
        return None
    
    def _detect_type_wrapper(self, node: ast.Call) -> Optional[str]:
        """Detect if getenv is wrapped in a type conversion function."""
        # This requires checking the parent node, which AST doesn't track
        # We'll use a simplified heuristic based on the source line
        try:
            line = self.source_lines[node.lineno - 1]
            if "int(" in line and "getenv" in line:
                return "int"
            elif "float(" in line and "getenv" in line:
                return "float"
            elif "bool(" in line and "getenv" in line:
                return "bool"
        except (IndexError, AttributeError):
            pass
        return None
    
    def _extract_inline_comment(self, line_number: int) -> Optional[str]:
        """Extract inline comment from the source line."""
        try:
            line = self.source_lines[line_number - 1]
            if "#" in line:
                comment_start = line.index("#")
                comment = line[comment_start + 1:].strip()
                # Filter out common non-descriptive comments
                if comment and not comment.startswith("noqa") and not comment.startswith("type:"):
                    return comment
        except (IndexError, ValueError):
            pass
        return None
    
    def _add_env_var(
        self,
        name: str,
        default_value: Optional[str],
        line_number: int,
        type_hint: Optional[str] = None
    ):
        """Add discovered env var, avoiding duplicates."""
        if name in self.seen:
            # Update usage count for existing variable
            for var in self.env_vars:
                if var.name == name:
                    var.usage_count += 1
            return
        
        self.seen.add(name)
        
        # Detect if sensitive
        is_sensitive = EnvVariable.detect_sensitive(name)
        
        # Detect category
        category = EnvVariable.detect_category(name)
        
        # Try to extract description from inline comment
        description = self._extract_inline_comment(line_number)
        
        env_var = EnvVariable(
            name=name,
            default_value=default_value,
            type_hint=type_hint,
            required=(default_value is None),
            source_file=self.source_file,
            line_number=line_number,
            description=description,
            is_sensitive=is_sensitive,
            category=category
        )
        
        self.env_vars.append(env_var)


class PythonScanner:
    """
    Scanner for detecting environment variables in Python source files.
    
    Uses AST parsing to accurately detect os.getenv(), os.environ.get(),
    and os.environ[] patterns.
    
    Example:
        scanner = PythonScanner()
        variables = scanner.scan_file("config.py")
        for var in variables:
            print(f"{var.name}: {var.default_value}")
    """
    
    EXTENSIONS = {".py"}
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
    
    def scan_file(self, file_path: str) -> List[EnvVariable]:
        """
        Scan a single Python file for environment variables.
        
        Args:
            file_path: Path to the Python file to scan
            
        Returns:
            List of discovered EnvVariable objects
        """
        path = Path(file_path)
        
        if not path.exists():
            self.errors.append(f"File not found: {file_path}")
            return []
        
        if path.suffix not in self.EXTENSIONS:
            return []
        
        try:
            source = path.read_text(encoding='utf-8')
            tree = ast.parse(source, filename=file_path)
            visitor = PythonEnvVisitor(str(path), source)
            visitor.visit(tree)
            return visitor.env_vars
        except SyntaxError as e:
            self.errors.append(f"Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            self.errors.append(f"Error scanning {file_path}: {e}")
            return []
    
    def scan_directory(
        self,
        directory: str,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[EnvVariable]:
        """
        Recursively scan a directory for Python files.
        
        Args:
            directory: Path to the directory to scan
            exclude_patterns: List of patterns to exclude (e.g., ["**/venv/**"])
            
        Returns:
            List of all discovered EnvVariable objects
        """
        if exclude_patterns is None:
            exclude_patterns = [
                "**/venv/**",
                "**/.venv/**",
                "**/node_modules/**",
                "**/__pycache__/**",
                "**/dist/**",
                "**/build/**",
                "**/.git/**",
            ]
        
        all_vars: List[EnvVariable] = []
        seen_names: Set[str] = set()
        
        dir_path = Path(directory)
        if not dir_path.exists():
            self.errors.append(f"Directory not found: {directory}")
            return []
        
        for py_file in dir_path.rglob("*.py"):
            # Check exclude patterns
            should_exclude = False
            for pattern in exclude_patterns:
                if py_file.match(pattern):
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
            
            file_vars = self.scan_file(str(py_file))
            
            # Deduplicate across files
            for var in file_vars:
                if var.name not in seen_names:
                    seen_names.add(var.name)
                    all_vars.append(var)
                else:
                    # Update usage count for existing variable
                    for existing in all_vars:
                        if existing.name == var.name:
                            existing.usage_count += 1
                            break
        
        return all_vars
