"""
Parser for .env and .env.example files.

This module handles reading and parsing existing environment files,
preserving comments, sections, and formatting information.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class EnvLine:
    """Represents a single line in an .env file."""
    line_number: int
    raw: str
    is_comment: bool = False
    is_blank: bool = False
    is_section_header: bool = False
    key: Optional[str] = None
    value: Optional[str] = None
    inline_comment: Optional[str] = None
    preceding_comments: List[str] = field(default_factory=list)


@dataclass  
class ParsedEnvFile:
    """Result of parsing an .env file."""
    path: str
    lines: List[EnvLine] = field(default_factory=list)
    variables: Dict[str, EnvLine] = field(default_factory=dict)
    sections: Dict[str, List[str]] = field(default_factory=dict)
    
    @property
    def variable_names(self) -> List[str]:
        """Get list of all variable names in order."""
        return [line.key for line in self.lines if line.key]


class EnvFileParser:
    """
    Parser for .env and .env.example files.
    
    Handles:
    - Key=value pairs
    - Comments (# style)
    - Section headers (# === SECTION ===)
    - Inline comments
    - Quoted values
    - Multiline values (basic support)
    """
    
    # Regex for parsing env lines
    KEY_VALUE_PATTERN = re.compile(
        r'^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$'
    )
    
    # Pattern for section headers
    SECTION_HEADER_PATTERN = re.compile(
        r'^#\s*={3,}\s*(.+?)\s*={3,}\s*$'
    )
    
    def __init__(self):
        pass
    
    def parse_file(self, file_path: str) -> ParsedEnvFile:
        """
        Parse an .env file.
        
        Args:
            file_path: Path to the .env file
            
        Returns:
            ParsedEnvFile containing all parsed data
        """
        path = Path(file_path)
        result = ParsedEnvFile(path=str(path))
        
        if not path.exists():
            return result
        
        try:
            content = path.read_text(encoding='utf-8')
        except Exception:
            return result
        
        return self.parse_content(content, str(path))
    
    def parse_content(self, content: str, source_path: str = "") -> ParsedEnvFile:
        """
        Parse .env content from a string.
        
        Args:
            content: The .env file content
            source_path: Optional source path for reference
            
        Returns:
            ParsedEnvFile containing all parsed data
        """
        result = ParsedEnvFile(path=source_path)
        lines = content.split('\n')
        
        preceding_comments: List[str] = []
        current_section: Optional[str] = None
        
        for line_num, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            
            # Blank line
            if not line:
                env_line = EnvLine(
                    line_number=line_num,
                    raw=raw_line,
                    is_blank=True
                )
                result.lines.append(env_line)
                # Reset preceding comments on blank line
                if preceding_comments:
                    preceding_comments = []
                continue
            
            # Check for section header
            section_match = self.SECTION_HEADER_PATTERN.match(line)
            if section_match:
                current_section = section_match.group(1).strip()
                env_line = EnvLine(
                    line_number=line_num,
                    raw=raw_line,
                    is_comment=True,
                    is_section_header=True
                )
                result.lines.append(env_line)
                result.sections[current_section] = []
                preceding_comments = []
                continue
            
            # Comment line
            if line.startswith('#'):
                preceding_comments.append(line[1:].strip())
                env_line = EnvLine(
                    line_number=line_num,
                    raw=raw_line,
                    is_comment=True
                )
                result.lines.append(env_line)
                continue
            
            # Key=value line
            match = self.KEY_VALUE_PATTERN.match(line)
            if match:
                key = match.group('key')
                value_part = match.group('value')
                
                # Parse value and inline comment
                value, inline_comment = self._parse_value(value_part)
                
                env_line = EnvLine(
                    line_number=line_num,
                    raw=raw_line,
                    key=key,
                    value=value,
                    inline_comment=inline_comment,
                    preceding_comments=preceding_comments.copy()
                )
                
                result.lines.append(env_line)
                result.variables[key] = env_line
                
                if current_section:
                    result.sections[current_section].append(key)
                
                preceding_comments = []
                continue
            
            # Unknown line format - treat as comment
            env_line = EnvLine(
                line_number=line_num,
                raw=raw_line,
                is_comment=True
            )
            result.lines.append(env_line)
        
        return result
    
    def _parse_value(self, value_part: str) -> Tuple[str, Optional[str]]:
        """
        Parse the value portion, extracting the value and any inline comment.
        
        Args:
            value_part: The part after the = sign
            
        Returns:
            Tuple of (value, inline_comment)
        """
        value_part = value_part.strip()
        
        if not value_part:
            return "", None
        
        # Handle quoted values
        if value_part.startswith('"'):
            # Find closing quote
            match = re.match(r'^"((?:[^"\\]|\\.)*)"\s*(?:#\s*(.*))?$', value_part)
            if match:
                value = match.group(1)
                inline_comment = match.group(2)
                return value, inline_comment
        
        if value_part.startswith("'"):
            # Find closing quote
            match = re.match(r"^'([^']*)'\s*(?:#\s*(.*))?$", value_part)
            if match:
                value = match.group(1)
                inline_comment = match.group(2)
                return value, inline_comment
        
        # Unquoted value - check for inline comment
        if '#' in value_part:
            # Be careful not to split on # inside the value
            parts = value_part.split('#', 1)
            value = parts[0].strip()
            inline_comment = parts[1].strip() if len(parts) > 1 else None
            return value, inline_comment
        
        return value_part, None
    
    def get_comments_for_variable(
        self,
        parsed: ParsedEnvFile,
        var_name: str
    ) -> List[str]:
        """
        Get all comments associated with a variable.
        
        Args:
            parsed: Parsed env file
            var_name: Variable name to look up
            
        Returns:
            List of comment strings
        """
        if var_name not in parsed.variables:
            return []
        
        env_line = parsed.variables[var_name]
        comments = env_line.preceding_comments.copy()
        
        if env_line.inline_comment:
            comments.append(env_line.inline_comment)
        
        return comments
