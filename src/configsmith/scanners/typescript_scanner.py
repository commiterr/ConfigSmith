"""
TypeScript/JavaScript scanner for environment variable detection.

This module uses regex patterns to detect environment variable usage
in TypeScript and JavaScript files, including:
- process.env.VAR_NAME
- process.env["VAR_NAME"]
- Destructured { VAR_NAME } = process.env
- import.meta.env.VAR_NAME (Vite)
- Framework-specific patterns (React, Next.js, Vue)
"""

import re
from pathlib import Path
from typing import List, Optional, Set, Tuple
from configsmith.models import EnvVariable, VariableCategory


class TypeScriptScanner:
    """
    Scanner for detecting environment variables in TypeScript/JavaScript files.
    
    Uses regex patterns to detect various environment variable access patterns
    commonly used in JavaScript/TypeScript codebases.
    
    Example:
        scanner = TypeScriptScanner()
        variables = scanner.scan_file("config.ts")
        for var in variables:
            print(f"{var.name}: {var.default_value}")
    """
    
    EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
    
    # Regex patterns for detecting env vars
    PATTERNS = [
        # process.env.VAR_NAME
        (r'process\.env\.([A-Z][A-Z0-9_]*)', None),
        # process.env["VAR_NAME"] or process.env['VAR_NAME']
        (r'process\.env\[[\"\']([A-Z][A-Z0-9_]*)[\"\']\]', None),
        # import.meta.env.VAR_NAME (Vite)
        (r'import\.meta\.env\.([A-Z][A-Z0-9_]*)', None),
        # Deno.env.get("VAR_NAME")
        (r'Deno\.env\.get\([\"\']([A-Z][A-Z0-9_]*)[\"\']\)', None),
    ]
    
    # Pattern for extracting default values
    # process.env.VAR_NAME || 'default'
    DEFAULT_PATTERNS = [
        # process.env.VAR || 'default'
        r"process\.env\.([A-Z][A-Z0-9_]*)\s*\|\|\s*['\"]([^'\"]*)['\"]",
        # process.env.VAR ?? 'default'  
        r"process\.env\.([A-Z][A-Z0-9_]*)\s*\?\?\s*['\"]([^'\"]*)['\"]",
        # process.env["VAR"] || 'default'
        r"process\.env\[['\"]([A-Z][A-Z0-9_]*)['\"]]\s*\|\|\s*['\"]([^'\"]*)['\"]",
    ]
    
    # Destructuring pattern: const { VAR_NAME = 'default' } = process.env
    DESTRUCTURE_PATTERN = r"(?:const|let|var)\s*\{([^}]+)\}\s*=\s*process\.env"
    
    # Framework prefixes for special handling
    FRAMEWORK_PREFIXES = {
        "REACT_APP_": "React (Create React App)",
        "NEXT_PUBLIC_": "Next.js",
        "VITE_": "Vite",
        "VUE_APP_": "Vue CLI",
        "NUXT_": "Nuxt.js",
        "GATSBY_": "Gatsby",
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
    
    def scan_file(self, file_path: str) -> List[EnvVariable]:
        """
        Scan a single TypeScript/JavaScript file for environment variables.
        
        Args:
            file_path: Path to the file to scan
            
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
            content = path.read_text(encoding='utf-8')
            return self._scan_content(content, str(path))
        except Exception as e:
            self.errors.append(f"Error scanning {file_path}: {e}")
            return []
    
    def _scan_content(self, content: str, source_file: str) -> List[EnvVariable]:
        """Scan file content for environment variables."""
        env_vars: List[EnvVariable] = []
        seen: Set[str] = set()
        lines = content.split('\n')
        
        # Scan with default value patterns first
        for pattern in self.DEFAULT_PATTERNS:
            for match in re.finditer(pattern, content):
                var_name = match.group(1)
                default_value = match.group(2)
                
                if var_name not in seen:
                    seen.add(var_name)
                    line_num = self._get_line_number(content, match.start())
                    env_vars.append(self._create_env_var(
                        var_name, default_value, source_file, line_num, lines
                    ))
        
        # Scan for destructuring patterns
        for match in re.finditer(self.DESTRUCTURE_PATTERN, content, re.MULTILINE):
            destructured = match.group(1)
            line_num = self._get_line_number(content, match.start())
            
            # Parse destructured variables
            for var_def in destructured.split(','):
                var_def = var_def.strip()
                if not var_def:
                    continue
                
                # Handle default values: VAR_NAME = 'default'
                if '=' in var_def:
                    parts = var_def.split('=', 1)
                    var_name = parts[0].strip()
                    default_match = re.search(r"['\"]([^'\"]*)['\"]", parts[1])
                    default_value = default_match.group(1) if default_match else None
                else:
                    var_name = var_def.strip()
                    default_value = None
                
                # Clean up variable name
                var_name = var_name.strip()
                if var_name and var_name not in seen and re.match(r'^[A-Z][A-Z0-9_]*$', var_name):
                    seen.add(var_name)
                    env_vars.append(self._create_env_var(
                        var_name, default_value, source_file, line_num, lines
                    ))
        
        # Scan with basic patterns (no default value)
        for pattern, _ in self.PATTERNS:
            for match in re.finditer(pattern, content):
                var_name = match.group(1)
                
                if var_name not in seen:
                    seen.add(var_name)
                    line_num = self._get_line_number(content, match.start())
                    env_vars.append(self._create_env_var(
                        var_name, None, source_file, line_num, lines
                    ))
        
        return env_vars
    
    def _create_env_var(
        self,
        name: str,
        default_value: Optional[str],
        source_file: str,
        line_number: int,
        lines: List[str]
    ) -> EnvVariable:
        """Create an EnvVariable with detected metadata."""
        is_sensitive = EnvVariable.detect_sensitive(name)
        category = EnvVariable.detect_category(name)
        description = self._extract_comment(lines, line_number)
        
        # Detect framework from prefix
        framework = None
        for prefix, framework_name in self.FRAMEWORK_PREFIXES.items():
            if name.startswith(prefix):
                framework = framework_name
                break
        
        if framework and not description:
            description = f"Required by {framework}"
        
        return EnvVariable(
            name=name,
            default_value=default_value,
            type_hint=self._infer_type(default_value),
            required=(default_value is None),
            source_file=source_file,
            line_number=line_number,
            description=description,
            is_sensitive=is_sensitive,
            category=category
        )
    
    def _get_line_number(self, content: str, position: int) -> int:
        """Get line number from character position."""
        return content[:position].count('\n') + 1
    
    def _extract_comment(self, lines: List[str], line_number: int) -> Optional[str]:
        """Extract comment from the line or previous line."""
        try:
            # Check current line for inline comment
            line = lines[line_number - 1]
            if '//' in line:
                comment_start = line.index('//')
                comment = line[comment_start + 2:].strip()
                if comment:
                    return comment
            
            # Check previous line for comment
            if line_number > 1:
                prev_line = lines[line_number - 2].strip()
                if prev_line.startswith('//'):
                    return prev_line[2:].strip()
                # Handle JSDoc style comments
                if prev_line.startswith('*'):
                    return prev_line[1:].strip()
        except IndexError:
            pass
        return None
    
    def _infer_type(self, default_value: Optional[str]) -> Optional[str]:
        """Infer type from default value."""
        if default_value is None:
            return None
        
        # Check if it looks like a number
        try:
            int(default_value)
            return "int"
        except ValueError:
            pass
        
        try:
            float(default_value)
            return "float"
        except ValueError:
            pass
        
        # Check for boolean
        if default_value.lower() in ('true', 'false'):
            return "bool"
        
        return "string"
    
    def scan_directory(
        self,
        directory: str,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[EnvVariable]:
        """
        Recursively scan a directory for TypeScript/JavaScript files.
        
        Args:
            directory: Path to the directory to scan
            exclude_patterns: List of patterns to exclude
            
        Returns:
            List of all discovered EnvVariable objects
        """
        if exclude_patterns is None:
            exclude_patterns = [
                "**/node_modules/**",
                "**/dist/**",
                "**/build/**",
                "**/.next/**",
                "**/.nuxt/**",
                "**/coverage/**",
                "**/.git/**",
            ]
        
        all_vars: List[EnvVariable] = []
        seen_names: Set[str] = set()
        
        dir_path = Path(directory)
        if not dir_path.exists():
            self.errors.append(f"Directory not found: {directory}")
            return []
        
        for ext in self.EXTENSIONS:
            for ts_file in dir_path.rglob(f"*{ext}"):
                # Check exclude patterns
                should_exclude = False
                for pattern in exclude_patterns:
                    if ts_file.match(pattern):
                        should_exclude = True
                        break
                
                if should_exclude:
                    continue
                
                file_vars = self.scan_file(str(ts_file))
                
                # Deduplicate across files
                for var in file_vars:
                    if var.name not in seen_names:
                        seen_names.add(var.name)
                        all_vars.append(var)
                    else:
                        # Update usage count
                        for existing in all_vars:
                            if existing.name == var.name:
                                existing.usage_count += 1
                                break
        
        return all_vars
