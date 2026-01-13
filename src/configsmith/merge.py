"""
Merge logic for combining discovered variables with existing files.

This module provides functionality to intelligently merge environment
variables discovered from code scanning with existing .env.example files,
preserving comments and handling conflicts.
"""

from typing import List, Dict, Optional, Set, Tuple
from configsmith.models import EnvVariable
from configsmith.parser import EnvFileParser, ParsedEnvFile


class MergeResult:
    """Result of a merge operation."""
    
    def __init__(self):
        self.variables: List[EnvVariable] = []
        self.new_variables: List[str] = []
        self.updated_variables: List[str] = []
        self.preserved_variables: List[str] = []
        self.removed_variables: List[str] = []
        self.preserved_comments: Dict[str, List[str]] = {}
    
    @property
    def total_variables(self) -> int:
        return len(self.variables)


def merge_env_variables(
    scanned_vars: List[EnvVariable],
    existing_content: Optional[str] = None,
    preserve_unused: bool = False
) -> MergeResult:
    """
    Merge scanned variables with existing .env.example content.
    
    Priority order (highest to lowest):
    1. Scanned from code (source of truth)
    2. Existing .env.example (preserves comments and values)
    3. Default values from code
    
    Args:
        scanned_vars: Variables discovered from code scanning
        existing_content: Content of existing .env.example file
        preserve_unused: If True, keep variables not found in code
        
    Returns:
        MergeResult with merged variables and change tracking
    """
    result = MergeResult()
    parser = EnvFileParser()
    
    # Parse existing file if provided
    existing: Optional[ParsedEnvFile] = None
    if existing_content:
        existing = parser.parse_content(existing_content)
    
    # Build lookup from scanned variables
    scanned_lookup: Dict[str, EnvVariable] = {v.name: v for v in scanned_vars}
    processed: Set[str] = set()
    
    # Process scanned variables
    for var in scanned_vars:
        merged_var = var.model_copy()
        
        if existing and var.name in existing.variables:
            # Variable exists in both - merge
            existing_line = existing.variables[var.name]
            
            # Preserve comments from existing file
            comments = parser.get_comments_for_variable(existing, var.name)
            if comments:
                result.preserved_comments[var.name] = comments
                if not merged_var.description and comments:
                    merged_var.description = comments[0]
            
            # Keep existing value if no default in code
            if merged_var.default_value is None and existing_line.value:
                merged_var.default_value = existing_line.value
            
            result.preserved_variables.append(var.name)
        else:
            # New variable from code
            result.new_variables.append(var.name)
        
        result.variables.append(merged_var)
        processed.add(var.name)
    
    # Handle variables only in existing file
    if existing and preserve_unused:
        for var_name, env_line in existing.variables.items():
            if var_name not in processed:
                # Create EnvVariable from existing file
                legacy_var = EnvVariable(
                    name=var_name,
                    default_value=env_line.value,
                    source_file="existing .env.example",
                    description=env_line.inline_comment
                )
                result.variables.append(legacy_var)
                result.preserved_variables.append(var_name)
                processed.add(var_name)
                
                # Preserve comments
                comments = parser.get_comments_for_variable(existing, var_name)
                if comments:
                    result.preserved_comments[var_name] = comments
    elif existing:
        # Track removed variables
        for var_name in existing.variables:
            if var_name not in processed:
                result.removed_variables.append(var_name)
    
    return result


def deduplicate_variables(variables: List[EnvVariable]) -> List[EnvVariable]:
    """
    Remove duplicate variables, keeping the first occurrence.
    
    Args:
        variables: List of variables potentially containing duplicates
        
    Returns:
        Deduplicated list of variables
    """
    seen: Set[str] = set()
    result: List[EnvVariable] = []
    
    for var in variables:
        if var.name not in seen:
            seen.add(var.name)
            result.append(var)
        else:
            # Update usage count on existing variable
            for existing in result:
                if existing.name == var.name:
                    existing.usage_count += var.usage_count
                    break
    
    return result


def merge_and_generate(
    existing_content: str,
    scanned_vars: List[EnvVariable]
) -> str:
    """
    Merge scanned variables with existing content and generate output.
    
    This is a convenience function that combines merge and generation.
    
    Args:
        existing_content: Content of existing .env.example
        scanned_vars: Variables discovered from scanning
        
    Returns:
        Generated .env.example content as string
    """
    from configsmith.generator import EnvExampleGenerator
    
    # Merge variables
    merged = merge_env_variables(scanned_vars, existing_content)
    
    # Generate output
    generator = EnvExampleGenerator()
    return generator.generate(
        merged.variables,
        preserved_comments=merged.preserved_comments
    )
