# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

yt-dlp is a feature-rich command-line audio/video downloader forked from youtube-dl. It's a Python project with extensive extractor support for thousands of sites.

## Essential Commands

### Development Environment
- `python -m hatch env create` - Set up development environment with all dependencies
- `python -m hatch shell` - Activate the development environment

### Testing
- `python -m devscripts.run_tests` - Run all tests
- `python -m devscripts.run_tests core` - Run core tests only
- `python -m devscripts.run_tests download` - Run download tests
- `python -m devscripts.run_tests -k EXPRESSION` - Run tests matching expression
- `make test` - Alternative test command (runs pytest + linting)
- `make offlinetest` - Run tests without network (excludes download tests)

### Code Quality
- `ruff check .` - Run linting checks
- `ruff check --fix .` - Auto-fix linting issues where possible
- `autopep8 --diff .` - Check code formatting
- `autopep8 --in-place .` - Apply code formatting fixes
- `make codetest` - Run both ruff and autopep8 checks

### Building and Installation
- `make lazy-extractors` - Generate lazy extractor loading (required for development)
- `make` - Build everything (lazy-extractors, completions, docs)
- `make clean` - Clean build artifacts
- `python -m build` - Build distribution packages

### Development Scripts
- `python devscripts/make_lazy_extractors.py` - Regenerate lazy extractors
- `python devscripts/run_tests.py` - Advanced test runner with filtering options

## Architecture Overview

### Core Components

**YoutubeDL Class (`yt_dlp/YoutubeDL.py`)**
- Main orchestrator class that coordinates the entire download process
- Handles configuration, progress reporting, and error management
- Entry point for all download operations

**Extractors (`yt_dlp/extractor/`)**
- Each site has its own extractor class inheriting from `InfoExtractor`
- Extractors parse video metadata and extract download URLs
- Lazy loading system to avoid importing all extractors at startup
- Common base functionality in `yt_dlp/extractor/common.py`

**Downloaders (`yt_dlp/downloader/`)**
- Protocol-specific downloaders (HTTP, HLS, DASH, etc.)
- Fragment-based downloading for segmented media
- External downloader integration (aria2, wget, etc.)

**Post-processors (`yt_dlp/postprocessor/`)**
- Handle post-download operations (ffmpeg, metadata, thumbnails)
- Modular system for audio conversion, video processing, etc.

**Networking (`yt_dlp/networking/`)**
- HTTP request handling with retry logic and error management
- Cookie support and browser integration
- Proxy and authentication handling

### Key Development Patterns

**Extractor Development**
- New extractors should inherit from `InfoExtractor`
- Use `_download_webpage()` and `_search_regex()` for content extraction
- Return info dictionaries with standardized field names
- Test extractors thoroughly with real URLs

**Option Handling**
- All CLI options defined in `yt_dlp/options.py`
- Options validation in `yt_dlp/__init__.py:validate_options()`
- Convert CLI options to YoutubeDL parameters

**Plugin System**
- Plugins loaded from `yt_dlp_plugins/` directories
- Support for custom extractors and post-processors
- See plugin architecture in `yt_dlp/plugins.py`

## Testing Guidelines

### Extractor Tests
- Each extractor should have test cases in `test/test_download.py`
- Use `add_ie` decorator to register test cases
- Test with real URLs but avoid tests that download large files
- Mark download tests appropriately to allow offline testing

### Running Specific Tests
```bash
# Test specific extractor
python -m devscripts.run_tests YoutubeIE

# Test with pattern matching
python -m devscripts.run_tests -k "youtube and not live"

# Test specific file
python -m pytest test/test_utils.py
```

## Code Style Requirements

- Follow PEP 8 with line length of 120 characters
- Use ruff for linting (configuration in `pyproject.toml`)
- Use autopep8 for formatting (configuration in `pyproject.toml`)
- Imports organized by isort rules
- Type hints encouraged for new code

## Important Development Notes

- Always regenerate lazy extractors after adding/modifying extractors
- Test extractors with multiple URLs when possible
- Follow existing patterns for info extraction and error handling
- Maintain backward compatibility for public APIs
- Use the utils functions in `yt_dlp/utils/` for common operations
- Extractor regular expressions should be robust and handle edge cases