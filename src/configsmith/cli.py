"""
ConfigSmith CLI - Command Line Interface.

This module provides the main CLI entry point for ConfigSmith,
using Typer for argument parsing and Rich for beautiful output.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from configsmith import __version__
from configsmith.models import EnvVariable, ScanResult
from configsmith.scanners.python_scanner import PythonScanner
from configsmith.scanners.typescript_scanner import TypeScriptScanner
from configsmith.parser import EnvFileParser
from configsmith.merge import merge_env_variables, deduplicate_variables
from configsmith.generator import EnvExampleGenerator

# Initialize Typer app
app = typer.Typer(
    name="configsmith",
    help="🔧 ConfigSmith - Automatically generate .env.example files from source code",
    add_completion=False,
)

console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        rprint(f"[bold blue]ConfigSmith[/bold blue] version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """ConfigSmith - Generate .env.example from your codebase."""
    pass


@app.command()
def generate(
    path: str = typer.Argument(
        ".",
        help="Path to scan (file or directory)",
    ),
    output: str = typer.Option(
        ".env.example",
        "--output",
        "-o",
        help="Output file path",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Preview changes without writing",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        help="Show detailed output",
    ),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Create backup before overwriting",
    ),
    preserve_unused: bool = typer.Option(
        False,
        "--preserve-unused",
        help="Keep variables not found in code",
    ),
    report: bool = typer.Option(
        False,
        "--report",
        "-r",
        help="Generate detailed report",
    ),
):
    """
    Generate .env.example from source code.
    
    Scans Python and TypeScript/JavaScript files for environment
    variable usage and generates a documented .env.example file.
    """
    console.print()
    console.print(Panel.fit(
        "[bold blue]🔍 ConfigSmith[/bold blue] - Scanning for environment variables...",
        border_style="blue"
    ))
    console.print()
    
    scan_path = Path(path).resolve()
    
    if not scan_path.exists():
        console.print(f"[red]Error: Path not found: {path}[/red]")
        raise typer.Exit(1)
    
    # Initialize scanners
    python_scanner = PythonScanner(verbose=verbose)
    ts_scanner = TypeScriptScanner(verbose=verbose)
    
    all_vars: List[EnvVariable] = []
    python_count = 0
    ts_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Scan Python files
        task = progress.add_task("📂 Scanning Python files...", total=None)
        if scan_path.is_file():
            if scan_path.suffix == ".py":
                py_vars = python_scanner.scan_file(str(scan_path))
                all_vars.extend(py_vars)
                python_count = 1 if py_vars else 0
        else:
            py_vars = python_scanner.scan_directory(str(scan_path))
            all_vars.extend(py_vars)
            python_count = len(list(scan_path.rglob("*.py")))
        progress.update(task, completed=True)
        
        # Scan TypeScript/JavaScript files
        task = progress.add_task("📂 Scanning TypeScript/JS files...", total=None)
        if scan_path.is_file():
            if scan_path.suffix in TypeScriptScanner.EXTENSIONS:
                ts_vars = ts_scanner.scan_file(str(scan_path))
                all_vars.extend(ts_vars)
                ts_count = 1 if ts_vars else 0
        else:
            ts_vars = ts_scanner.scan_directory(str(scan_path))
            all_vars.extend(ts_vars)
            ts_count = sum(1 for ext in TypeScriptScanner.EXTENSIONS 
                          for _ in scan_path.rglob(f"*{ext}"))
        progress.update(task, completed=True)
    
    # Deduplicate variables
    all_vars = deduplicate_variables(all_vars)
    
    if verbose:
        for var in all_vars:
            console.print(f"  ✓ {var.source_file}: {var.name}")
    
    # Check for existing .env.example
    output_path = Path(output)
    existing_content: Optional[str] = None
    
    if output_path.exists():
        existing_content = output_path.read_text(encoding='utf-8')
    
    # Merge with existing
    merge_result = merge_env_variables(
        all_vars,
        existing_content,
        preserve_unused=preserve_unused
    )
    
    # Print results
    console.print()
    console.print("[bold]📊 Results:[/bold]")
    
    table = Table(show_header=False, box=None)
    table.add_column("Label", style="dim")
    table.add_column("Value", style="bold")
    
    table.add_row("Python files scanned:", str(python_count))
    table.add_row("TypeScript/JS files scanned:", str(ts_count))
    table.add_row("Total variables discovered:", str(len(all_vars)))
    table.add_row("New variables:", str(len(merge_result.new_variables)))
    table.add_row("Preserved variables:", str(len(merge_result.preserved_variables)))
    
    if merge_result.removed_variables:
        table.add_row("Removed (not in code):", str(len(merge_result.removed_variables)))
    
    console.print(table)
    console.print()
    
    # Generate output
    generator = EnvExampleGenerator()
    output_content = generator.generate(
        merge_result.variables,
        preserved_comments=merge_result.preserved_comments
    )
    
    if dry_run:
        console.print("[yellow]🔍 Dry run - preview of .env.example:[/yellow]")
        console.print()
        console.print(Panel(output_content, title=output, border_style="yellow"))
        console.print()
        console.print("[yellow]No changes written (dry run mode)[/yellow]")
    else:
        # Create backup if file exists
        if backup and output_path.exists():
            backup_path = output_path.with_suffix(".example.backup")
            backup_path.write_text(existing_content or "", encoding='utf-8')
            console.print(f"[dim]💾 Backup saved to: {backup_path}[/dim]")
        
        # Write output
        output_path.write_text(output_content, encoding='utf-8')
        console.print(f"[green]✨ Generated:[/green] {output}")
    
    # Show new variables
    if merge_result.new_variables and verbose:
        console.print()
        console.print("[bold]New variables added:[/bold]")
        for name in merge_result.new_variables:
            console.print(f"  [green]+[/green] {name}")
    
    # Generate report if requested
    if report:
        report_path = f"configsmith-report-{datetime.now().strftime('%Y-%m-%d')}.json"
        _generate_report(merge_result, all_vars, report_path)
        console.print(f"[dim]📝 Report saved to: {report_path}[/dim]")
    
    console.print()
    console.print("[bold green]✅ Done![/bold green] Review .env.example for changes.")


def _generate_report(merge_result, all_vars: List[EnvVariable], output_path: str):
    """Generate a JSON report of the scan."""
    import json
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_variables": len(merge_result.variables),
        "new_variables": merge_result.new_variables,
        "preserved_variables": merge_result.preserved_variables,
        "removed_variables": merge_result.removed_variables,
        "variables": [
            {
                "name": v.name,
                "default_value": v.default_value,
                "type": v.type_hint,
                "required": v.required,
                "sensitive": v.is_sensitive,
                "category": v.category.value,
                "source": v.source_file,
                "line": v.line_number,
            }
            for v in all_vars
        ]
    }
    
    Path(output_path).write_text(json.dumps(report, indent=2), encoding='utf-8')


@app.command()
def validate(
    env_file: str = typer.Argument(
        ".env",
        help="Path to .env file to validate",
    ),
    example_file: str = typer.Option(
        ".env.example",
        "--example",
        "-e",
        help="Path to .env.example file",
    ),
):
    """
    Validate .env file against .env.example.
    
    Checks that all required variables are present and
    reports any missing or extra variables.
    """
    console.print()
    console.print("[bold blue]🔍 Validating environment file...[/bold blue]")
    console.print()
    
    env_path = Path(env_file)
    example_path = Path(example_file)
    
    if not example_path.exists():
        console.print(f"[red]Error: Example file not found: {example_file}[/red]")
        raise typer.Exit(1)
    
    parser = EnvFileParser()
    
    example_parsed = parser.parse_file(str(example_path))
    example_vars = set(example_parsed.variable_names)
    
    if env_path.exists():
        env_parsed = parser.parse_file(str(env_path))
        env_vars = set(env_parsed.variable_names)
    else:
        env_vars = set()
        console.print(f"[yellow]Warning: {env_file} not found[/yellow]")
    
    missing = example_vars - env_vars
    extra = env_vars - example_vars
    
    if missing:
        console.print("[red]❌ Missing variables:[/red]")
        for name in sorted(missing):
            console.print(f"   {name}")
    
    if extra:
        console.print("[yellow]⚠️  Extra variables (not in example):[/yellow]")
        for name in sorted(extra):
            console.print(f"   {name}")
    
    if not missing and not extra:
        console.print("[green]✅ All variables present and accounted for![/green]")
        raise typer.Exit(0)
    elif missing:
        console.print()
        console.print(f"[red]Validation failed: {len(missing)} missing variable(s)[/red]")
        raise typer.Exit(1)
    else:
        console.print()
        console.print("[green]✅ All required variables present[/green]")
        raise typer.Exit(0)


@app.command()
def init(
    path: str = typer.Argument(
        ".",
        help="Project path",
    ),
):
    """
    Initialize ConfigSmith in a project.
    
    Creates a .configsmith.yml configuration file with
    sensible defaults.
    """
    config_content = '''# ConfigSmith Configuration
# See https://github.com/commiterr/ConfigSmith for documentation

scan:
  include:
    - src/
    - lib/
    - app/
    - server/
  
  exclude:
    - node_modules/
    - venv/
    - .venv/
    - dist/
    - build/
    - __pycache__/
    - "*.test.*"
    - "*.spec.*"

generate:
  output: .env.example
  backup: true
  sort: alphabetical
  group_by: category

  include:
    source_file: true
    type_hint: true
    default_value: true
'''
    
    config_path = Path(path) / ".configsmith.yml"
    
    if config_path.exists():
        console.print(f"[yellow]Config file already exists: {config_path}[/yellow]")
        raise typer.Exit(1)
    
    config_path.write_text(config_content, encoding='utf-8')
    console.print(f"[green]✨ Created:[/green] {config_path}")
    console.print()
    console.print("Edit .configsmith.yml to customize scanning behavior.")
    console.print("Run [bold]configsmith generate[/bold] to scan your project.")


if __name__ == "__main__":
    app()
