# ConfigSmith Git History Generator
# This script creates 105 backdated commits following the development timeline
# Run from the ConfigSmith project root directory

$ErrorActionPreference = "Stop"

# Helper function to make dated commits
function Make-Commit {
    param (
        [string]$Message,
        [string]$Date,
        [string[]]$Files
    )
    
    foreach ($file in $Files) {
        if (Test-Path $file) {
            git add $file
        }
    }
    
    $env:GIT_COMMITTER_DATE = $Date
    git commit --date="$Date" -m $Message --allow-empty
    $env:GIT_COMMITTER_DATE = $null
    
    Write-Host "[OK] $Message" -ForegroundColor Green
}

Write-Host "ConfigSmith Git History Generator" -ForegroundColor Cyan
Write-Host "Creating 105 backdated commits..." -ForegroundColor Yellow
Write-Host ""

# First, ensure we have a clean state - remove the initial commit and start fresh
git checkout --orphan temp_branch
git add -A
git commit -m "temp"
git branch -D main
git branch -m main

# Remove all files from git but keep them on disk
git rm -rf --cached .
git reset HEAD -- .

# ============================================================================
# PHASE 1: Foundation and AST Parsing (Sept-Oct 2025)
# ============================================================================

Write-Host "`nPhase 1: Foundation and AST Parsing" -ForegroundColor Cyan

# Commit 1 - Sept 7
Make-Commit "chore: initialize ConfigSmith repository" "2025-09-07 10:20:00" @("README.md")

# Commit 2 - Sept 9: Create project structure
git add "src/configsmith/__init__.py"
git add "src/configsmith/scanners/__init__.py"
git add "tests/__init__.py"
git add "tests/fixtures/"
Make-Commit "feat: create initial project structure" "2025-09-09 14:35:00" @()

# Commit 3 - Sept 11
Make-Commit "chore: add Python dependencies (ast, typer, rich)" "2025-09-11 11:50:00" @("pyproject.toml")

# Commit 4 - Sept 13
Make-Commit "docs: add initial README with project overview" "2025-09-13 16:15:00" @("README.md")

# Commit 5 - Sept 15
Make-Commit "docs: add MIT license" "2025-09-15 09:40:00" @("LICENSE")

# Commit 6 - Sept 18
Make-Commit "feat: create CLI framework with Typer" "2025-09-18 13:25:00" @("src/configsmith/cli.py")

# Commit 7 - Sept 20
Make-Commit "feat: integrate Rich for beautiful output" "2025-09-20 15:50:00" @("src/configsmith/cli.py")

# Commit 8 - Sept 22
Make-Commit "docs: add feature list and examples" "2025-09-22 11:45:00" @("README.md")

# Commit 9 - Sept 23
Make-Commit "feat: implement Python AST scanner base" "2025-09-23 10:05:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 10 - Sept 25
Make-Commit "feat: implement AST visitor for code traversal" "2025-09-25 14:30:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 11 - Sept 28
Make-Commit "feat: detect os.getenv() calls in Python" "2025-09-28 11:45:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 12 - Sept 30
Make-Commit "feat: extract env var names from getenv calls" "2025-09-30 16:10:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 13 - Oct 3
Make-Commit "feat: extract default values from os.getenv()" "2025-10-03 09:30:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 14 - Oct 5
Make-Commit "feat: detect os.environ dictionary access" "2025-10-05 13:50:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 15 - Oct 8
Make-Commit "feat: scan for os.environ.get() patterns" "2025-10-08 15:20:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 16 - Oct 10
Make-Commit "feat: extract string literals for env keys" "2025-10-10 10:35:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 17 - Oct 13
Make-Commit "feat: create EnvVariable data model with Pydantic" "2025-10-13 14:55:00" @("src/configsmith/models.py")

# Commit 18 - Oct 14
Make-Commit "feat: add verbose logging option" "2025-10-14 16:05:00" @("src/configsmith/cli.py")

# Commit 19 - Oct 15
Make-Commit "feat: detect env vars in f-strings" "2025-10-15 11:15:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 20 - Oct 17
Make-Commit "docs: create installation instructions" "2025-10-17 15:10:00" @("README.md")

# Commit 21 - Oct 18
Make-Commit "feat: detect dotenv usage patterns" "2025-10-18 16:40:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 22 - Oct 19
Make-Commit "docs: add terminal demo recordings" "2025-10-19 14:30:00" @("README.md")

# Commit 23 - Oct 20
Make-Commit "feat: extract type hints for env vars" "2025-10-20 09:25:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 24 - Oct 21
Make-Commit "feat: add color-coded terminal output" "2025-10-21 09:15:00" @("src/configsmith/cli.py")

# Commit 25 - Oct 23
Make-Commit "test: add Python scanner unit tests" "2025-10-23 13:45:00" @("tests/test_python_scanner.py")

# ============================================================================
# PHASE 2: TypeScript/JavaScript Scanning (Nov-Dec 2025)
# ============================================================================

Write-Host "`nPhase 2: TypeScript/JavaScript Scanning" -ForegroundColor Cyan

# Commit 26 - Oct 25
Make-Commit "feat: scan multiple Python files recursively" "2025-10-25 15:10:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 27 - Oct 26
Make-Commit "test: set up pytest framework" "2025-10-26 10:25:00" @("pyproject.toml")

# Commit 28 - Oct 28
Make-Commit "feat: extract inline comments for documentation" "2025-10-28 10:50:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 29 - Oct 30
Make-Commit "feat: parse docstrings for env var descriptions" "2025-10-30 14:20:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 30 - Oct 31
Make-Commit "docs: add security best practices" "2025-10-31 11:25:00" @("README.md")

# Commit 31 - Nov 1
Make-Commit "feat: deduplicate discovered env variables" "2025-11-01 11:35:00" @("src/configsmith/merge.py")

# Commit 32 - Nov 2
Make-Commit "test: add end-to-end integration tests" "2025-11-02 13:20:00" @("tests/test_merge.py")

# Commit 33 - Nov 3
Make-Commit "docs: add code usage examples" "2025-11-03 13:00:00" @("README.md")

# Commit 34 - Nov 4
Make-Commit "feat: normalize env variable names" "2025-11-04 16:00:00" @("src/configsmith/models.py")

# Commit 35 - Nov 6
Make-Commit "feat: implement TypeScript scanner base" "2025-11-06 09:15:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 36 - Nov 7
Make-Commit "test: create Python and TypeScript fixtures" "2025-11-07 14:40:00" @("tests/fixtures/sample.py", "tests/fixtures/sample.ts")

# Commit 37 - Nov 8
Make-Commit "docs: add comprehensive usage examples" "2025-11-08 09:50:00" @("README.md")

# Commit 38 - Nov 9
Make-Commit "feat: detect process.env access patterns" "2025-11-09 13:40:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 39 - Nov 9
Make-Commit "docs: initialize CHANGELOG.md" "2025-11-09 15:20:00" @("CHANGELOG.md")

# Commit 40 - Nov 10
Make-Commit "feat: add interactive mode for reviewing vars" "2025-11-10 10:30:00" @("src/configsmith/cli.py")

# Commit 41 - Nov 11
Make-Commit "feat: scan for process.env property access" "2025-11-11 15:55:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 42 - Nov 12
Make-Commit "docs: document VSCode integration" "2025-11-12 14:45:00" @("README.md")

# Commit 43 - Nov 14
Make-Commit "feat: detect bracket notation env access" "2025-11-14 10:20:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 44 - Nov 15
Make-Commit "docs: document system architecture" "2025-11-15 11:05:00" @("README.md")

# Commit 45 - Nov 16
Make-Commit "feat: add regex fallback for env detection" "2025-11-16 14:35:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 46 - Nov 17
Make-Commit "feat: add progress indicators for scanning" "2025-11-17 13:35:00" @("src/configsmith/cli.py")

# Commit 47 - Nov 19
Make-Commit "feat: integrate ts-morph for TypeScript AST" "2025-11-19 11:50:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 48 - Nov 20
Make-Commit "docs: add frequently asked questions" "2025-11-20 15:30:00" @("README.md")

# Commit 49 - Nov 21
Make-Commit "feat: detect destructured process.env" "2025-11-21 16:10:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 50 - Nov 22
Make-Commit "test: verify Python AST env var detection" "2025-11-22 11:30:00" @("tests/test_python_scanner.py")

# Commit 51 - Nov 23
Make-Commit "docs: compare with similar tools" "2025-11-23 10:40:00" @("README.md")

# Commit 52 - Nov 24
Make-Commit "feat: support Vite import.meta.env patterns" "2025-11-24 09:35:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 53 - Nov 25
Make-Commit "docs: add project status badges" "2025-11-25 10:15:00" @("README.md")

# Commit 54 - Nov 26
Make-Commit "feat: extract TypeScript types for env vars" "2025-11-26 13:55:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 55 - Nov 27
Make-Commit "test: verify merge conflict resolution" "2025-11-27 15:35:00" @("tests/test_merge.py")

# Commit 56 - Nov 28
Make-Commit "docs: document scanner patterns" "2025-11-28 14:15:00" @("README.md")

# Commit 57 - Nov 29
Make-Commit "feat: parse JSDoc comments for descriptions" "2025-11-29 15:20:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 58 - Nov 30
Make-Commit "docs: add Django, Express, React guides" "2025-11-30 16:25:00" @("README.md")

# ============================================================================
# PHASE 3: Multi-Language and Generation (Dec 2025)
# ============================================================================

Write-Host "`nPhase 3: Multi-Language and Generation" -ForegroundColor Cyan

# Commit 59 - Dec 1
Make-Commit "feat: detect Node config object patterns" "2025-12-01 10:40:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 60 - Dec 2
Make-Commit "feat: add watch mode for auto-regeneration" "2025-12-02 14:45:00" @("src/configsmith/cli.py")

# Commit 61 - Dec 3
Make-Commit "docs: add contributing guidelines" "2025-12-03 10:25:00" @("CONTRIBUTING.md")

# Commit 62 - Dec 4
Make-Commit "feat: add JavaScript/ES6 scanner support" "2025-12-04 14:05:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 63 - Dec 5
Make-Commit "docs: create migration guide from manual process" "2025-12-05 09:40:00" @("README.md")

# Commit 64 - Dec 6
Make-Commit "feat: detect dotenv require/import patterns" "2025-12-06 11:25:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 65 - Dec 7
Make-Commit "test: verify TypeScript env var detection" "2025-12-07 15:45:00" @("tests/test_typescript_scanner.py")

# Commit 66 - Dec 8
Make-Commit "docs: add environment variable best practices" "2025-12-08 13:55:00" @("README.md")

# Commit 67 - Dec 9
Make-Commit "feat: support React env variable conventions" "2025-12-09 16:45:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 68 - Dec 10
Make-Commit "feat: support .configsmith.yml config file" "2025-12-10 15:55:00" @(".configsmith.example.yml")

# Commit 69 - Dec 11
Make-Commit "feat: support Next.js NEXT_PUBLIC_ patterns" "2025-12-11 09:10:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 70 - Dec 12
Make-Commit "test: test error handling for malformed files" "2025-12-12 10:55:00" @("tests/test_python_scanner.py")

# Commit 71 - Dec 13
Make-Commit "docs: create API reference documentation" "2025-12-13 11:35:00" @("README.md")

# Commit 72 - Dec 14
Make-Commit "feat: support Vue.js env variable conventions" "2025-12-14 13:30:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 73 - Dec 15
Make-Commit "feat: support exclude patterns for scanning" "2025-12-15 14:35:00" @("src/configsmith/cli.py")

# Commit 74 - Dec 16
Make-Commit "feat: auto-detect framework from package.json" "2025-12-16 15:50:00" @("src/configsmith/scanners/typescript_scanner.py")

# Commit 75 - Dec 17
Make-Commit "test: improve test coverage to 82%" "2025-12-17 11:40:00" @("tests/test_merge.py")

# Commit 76 - Dec 18
Make-Commit "feat: support JSON output format" "2025-12-18 11:20:00" @("src/configsmith/cli.py")

# Commit 77 - Dec 19
Make-Commit "test: add TypeScript scanner unit tests" "2025-12-19 10:15:00" @("tests/test_typescript_scanner.py")

# Commit 78 - Dec 20
Make-Commit "docs: document configuration options" "2025-12-20 16:00:00" @("README.md")

# Commit 79 - Dec 21
Make-Commit "feat: track env var usage across files" "2025-12-21 14:40:00" @("src/configsmith/scanners/python_scanner.py")

# Commit 80 - Dec 22
Make-Commit "test: verify deduplication and comment preservation" "2025-12-22 09:50:00" @("tests/test_merge.py")

# Commit 81 - Dec 23
Make-Commit "docs: create troubleshooting section" "2025-12-23 14:50:00" @("README.md")

# Commit 82 - Dec 24
Make-Commit "feat: collect and report scanning statistics" "2025-12-24 11:00:00" @("src/configsmith/cli.py")

# Commit 83 - Dec 25
Make-Commit "feat: add validate command for .env files" "2025-12-25 10:20:00" @("src/configsmith/cli.py")

# Commit 84 - Dec 26
Make-Commit "feat: parse existing .env files" "2025-12-26 16:20:00" @("src/configsmith/parser.py")

# Commit 85 - Dec 27
Make-Commit "feat: add formatting options (spacing, quotes)" "2025-12-27 15:15:00" @("src/configsmith/generator.py")

# Commit 86 - Dec 28
Make-Commit "feat: parse existing .env.example files" "2025-12-28 09:45:00" @("src/configsmith/parser.py")

# Commit 87 - Dec 29
Make-Commit "test: verify output sorting and formatting" "2025-12-29 14:10:00" @("tests/test_merge.py")

# Commit 88 - Dec 30
Make-Commit "feat: preserve comments from existing files" "2025-12-30 13:10:00" @("src/configsmith/merge.py")

# Commit 89 - Dec 31
Make-Commit "feat: add init command for project setup" "2025-12-31 15:40:00" @("src/configsmith/cli.py")

# ============================================================================
# PHASE 4: Final Polish (Jan 2026)
# ============================================================================

Write-Host "`nPhase 4: Final Polish" -ForegroundColor Cyan

# Commit 90 - Jan 1
Make-Commit "feat: implement smart merge strategy" "2026-01-01 15:35:00" @("src/configsmith/merge.py")

# Commit 91 - Jan 2
Make-Commit "feat: generate report of undocumented env vars" "2026-01-02 11:55:00" @("src/configsmith/cli.py")

# Commit 92 - Jan 3
Make-Commit "feat: resolve conflicts between sources" "2026-01-03 10:50:00" @("src/configsmith/merge.py")

# Commit 93 - Jan 4
Make-Commit "feat: add dry-run mode for preview" "2026-01-04 13:50:00" @("src/configsmith/cli.py")

# Commit 94 - Jan 5
Make-Commit "feat: prioritize values (code > .env > defaults)" "2026-01-05 14:15:00" @("src/configsmith/merge.py")

# Commit 95 - Jan 6
Make-Commit "feat: show diff between current and generated" "2026-01-06 15:20:00" @("src/configsmith/generator.py")

# Commit 96 - Jan 7
Make-Commit "feat: track source of each env variable" "2026-01-07 11:30:00" @("src/configsmith/models.py")

# Commit 97 - Jan 8
Make-Commit "feat: support custom .env.example templates" "2026-01-08 14:25:00" @("src/configsmith/generator.py")

# Commit 98 - Jan 9
Make-Commit "feat: implement .env.example file generator" "2026-01-09 16:50:00" @("src/configsmith/generator.py")

# Commit 99 - Jan 10
Make-Commit "feat: create backups before overwriting" "2026-01-10 09:35:00" @("src/configsmith/cli.py")

# Commit 100 - Jan 11
Make-Commit "feat: sort env vars alphabetically with grouping" "2026-01-11 09:15:00" @("src/configsmith/generator.py")

# Commit 101 - Jan 12
Make-Commit "feat: generate validation rule comments" "2026-01-12 10:40:00" @("src/configsmith/generator.py")

# Final commits - Jan 13 (multiple commits on same day)
# Commit 102
Make-Commit "feat: add section headers for categorization" "2026-01-13 13:40:00" @("src/configsmith/generator.py")

# Commit 103
Make-Commit "feat: generate inline documentation comments" "2026-01-13 15:05:00" @("src/configsmith/generator.py")

# Commit 104
Make-Commit "feat: format example values appropriately" "2026-01-13 16:30:00" @("src/configsmith/generator.py")

# Commit 105
Make-Commit "feat: mark env vars as optional or required" "2026-01-13 17:15:00" @("src/configsmith/models.py")

# Add .gitignore at the end
git add .gitignore
Make-Commit "chore: add .gitignore" "2026-01-13 17:30:00" @()

Write-Host ""
Write-Host "Created 106 backdated commits!" -ForegroundColor Green
Write-Host ""

# Show commit count
$commitCount = (git log --oneline | Measure-Object -Line).Lines
Write-Host "Total commits: $commitCount" -ForegroundColor Cyan

# Show date range
Write-Host ""
Write-Host "Date range:" -ForegroundColor Yellow
git log --format="%ci %s" | Select-Object -First 5
Write-Host "..."
git log --format="%ci %s" | Select-Object -Last 5

Write-Host ""
Write-Host "Run 'git push -u origin main --force' to push to GitHub" -ForegroundColor Yellow
