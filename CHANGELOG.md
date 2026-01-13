# Changelog

All notable changes to ConfigSmith will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-13

### Added

- **Python AST Scanner**
  - Detect `os.getenv()` with default values
  - Detect `os.environ.get()` patterns
  - Detect `os.environ[]` subscript access
  - Extract type hints from wrapper functions (e.g., `int(os.getenv(...))`)
  - Parse inline comments for descriptions

- **TypeScript/JavaScript Scanner**
  - Detect `process.env.VAR_NAME` access
  - Detect `process.env["VAR_NAME"]` bracket notation
  - Detect destructured `{ VAR } = process.env`
  - Support `import.meta.env` for Vite
  - Framework detection (React, Next.js, Vue, Nuxt, Gatsby)

- **Merge & Generation**
  - Smart merge with existing `.env.example` files
  - Preserve comments from existing files
  - Deduplicate variables across sources
  - Sort alphabetically with category grouping
  - Generate section headers
  - Include source file references
  - Mark sensitive variables with security warnings

- **CLI Commands**
  - `generate` - Scan and generate `.env.example`
  - `validate` - Check `.env` against `.env.example`
  - `init` - Create `.configsmith.yml` config

- **CLI Features**
  - Beautiful Rich terminal output
  - Dry-run mode for previewing changes
  - Automatic backup creation
  - Detailed reporting with `--report`
  - Verbose mode with `--verbose`

- **Configuration**
  - Support for `.configsmith.yml` config file
  - Customizable include/exclude patterns
  - Output formatting options

### Documentation

- Comprehensive README with examples
- Contributing guidelines
- MIT License

## [Unreleased]

### Planned

- Watch mode for auto-regeneration
- Interactive mode for reviewing variables
- VSCode extension snippet output
- YAML/TOML config file support
- Environment validation rules
