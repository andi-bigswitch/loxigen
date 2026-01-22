# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About LoxiGen

LoxiGen is a code generator that produces OpenFlow protocol libraries for multiple languages (C, Python3, Java, and Wireshark dissector). It parses wire protocol descriptions from input files and generates language-specific implementations supporting OpenFlow versions 1.0-1.5.

**Production-ready versions**: 1.0, 1.3.1, 1.4.1
**Experimental versions**: 1.1, 1.2, 1.5.1 (Java only)

LoxiGen has no runtime dependencies beyond Python 3. Running tests requires pytest and Maven (for Java tests).

## Build and Test Commands

### Generate Libraries

Generate all language backends:
```bash
make
```

Generate specific language:
```bash
make c          # C library
make python3    # Python3 library
make java       # Java library (openflowj)
make wireshark  # Wireshark dissector (experimental)
```

### Running Tests

Run all tests (required before submitting PRs):
```bash
make check-all
```

Individual test suites:
```bash
make check        # Python unit tests (uses pytest)
make check-c      # C library tests
make check-py3    # Python3 library tests
make check-java   # Java library tests (uses Maven)
```

Run Python unit tests directly:
```bash
pytest                    # Run all tests in utest/
pytest utest/test_*.py   # Run all unit tests
pytest -k test_name      # Run specific test by name
pytest utest/test_build_ir.py  # Run single test file
```

### Java-specific Commands

```bash
make package-java  # Build JAR package
make install-java  # Install to local Maven repository
make deploy-java   # Deploy to remote repository
cd loxi_output/openflowj && mvn test  # Run only Java tests
```

### Clean Build Artifacts

```bash
make clean  # Removes loxi_output directory and timestamp files
```

## Architecture Overview

### Code Generation Pipeline

1. **Input Processing**: Parse OpenFlow protocol definitions from `openflow_input/` directory
   - Base structs files (e.g., `openflow_input/structs-1.3`)
   - Extension files (e.g., `openflow_input/bsn*` for BigSwitch extensions)

2. **Frontend**: `loxi_front_end/` - Parse input files into intermediate representation (IR)
   - `parser.py`: Parse input syntax
   - `frontend.py`: Convert parsed AST to IR
   - `frontend_ir.py`: Frontend IR data structures

3. **IR Layer**: `loxi_ir/` - Unified intermediate representation across all versions
   - `ir.py`: Core IR data structures (OFClass, OFDataMember, etc.)
   - `unified.py`: Unify representations across OpenFlow versions

4. **Backend Code Generation**: Language-specific generators
   - `c_gen/`: C code generator
   - `java_gen/`: Java code generator (openflowj)
   - `py_gen/`: Python3 code generator
   - `wireshark_gen/`: Wireshark dissector generator

5. **Output**: Generated code in `loxi_output/<language>/`

### Key Entry Points

- `loxigen.py`: Main entry point - orchestrates the entire generation process
- `lang_c.py`, `lang_java.py`, `lang_python3.py`, `lang_wireshark.py`: Language-specific configuration defining what files to generate
- `loxi_globals.py`: Global state including OFVersions registry
- `cmdline.py`: Command-line argument processing

### Template System

Each backend uses templates in `<lang>_gen/templates/`:
- Templates use Tenjin templating engine (`tenjin.py`)
- `template_utils.py`: Helper functions for template rendering

### OpenFlow Version Support

Versions defined in `loxi_globals.py` OFVersions class:
- VERSION_1_0 through VERSION_1_5 (wire_version 1-6)
- Each version maps to specific wire protocol value and version string
- Target versions selected via command-line `--version-list` parameter

### Generated Output Structure

```
loxi_output/
  loci/          # C library (LOCI)
  pyloxi3/       # Python3 library
  openflowj/     # Java library (openflowj)
  wireshark/     # Wireshark dissector
```

## Input File Format

Input files in `openflow_input/` define OpenFlow protocol structures using a custom syntax:
- First line: `#version <wire_version>` (e.g., `#version 4` for OpenFlow 1.3)
- Enum definitions: `enum macro_definitions { ... }` for constants
- Struct definitions with fields: `type field_name;`
- Lists: `list(type) field_name;` for variable-length lists
- Arrays: `type[length] field_name;` for fixed-length arrays
- Version-specific files: `standard-<version>` (base protocol) and `bsn-<version>` (BigSwitch extensions)
- Special processing applied to openflow.h headers:
  - `ofp_header` instances are replaced with their contents inline
  - Flow modify operations split into separate objects (add, modify, modify_strict, delete, delete_strict)
  - Match structures renamed to be version-specific
  - Each action/instruction type becomes its own type

## Modification Workflow

When adding new OpenFlow features:

1. Add/modify struct definitions in `openflow_input/` for the relevant version
2. Run code generation: `make <language>`
3. Test generated code: `make check-<language>`
4. Verify all languages: `make check-all`

When modifying code generators:

1. Edit backend code in `<lang>_gen/` or templates in `<lang>_gen/templates/`
2. Regenerate: `make <language>`
3. Run tests: `make check-<language>` or `make check-all`

## Java Backend Details

- Pre-written code: `java_gen/pre-written/` - base classes and utilities that aren't generated
- Generated code merged with pre-written in `loxi_output/openflowj/`
- Generated sources placed in `gen-src/` subdirectory
- Uses Maven for build and dependency management (pom.xml in pre-written/)
- Package: `org.projectfloodlight.openflow.*`
- Eclipse workspace setup available via `make eclipse-workspace`

## Testing Infrastructure

LoxiGen has two test levels:

### 1. LoxiGen Unit Tests (`utest/`)
Python tests for the code generator itself (uses pytest):
- `test_parser.py`: Input file parser tests
- `test_frontend.py`: Frontend IR generation tests
- `test_build_ir.py`: Unified IR construction tests
- `test_generic_utils.py`: Utility function tests
- `test_test_data.py`: Test data validation
- Test data: `test_data/` directory with `.data` files

### 2. Generated Library Tests
Tests for the generated code in each language:
- **C tests**: `loxi_output/locitest/` - compiled and run via `make check-c`
- **Python3 tests**: `py_gen/tests3/` - run against generated pyloxi3 library
- **Java tests**: `java_gen/pre-written/src/test/` - JUnit tests run via Maven

## Direct Invocation

LoxiGen can be run directly without the Makefile:
```bash
./loxigen.py --install-dir=loxi_output --lang=c --version-list=1.0,1.3,1.4
./loxigen.py --install-dir=loxi_output --lang=python3
./loxigen.py --install-dir=loxi_output --lang=java
```

Command-line arguments handled by `cmdline.py`:
- `--install-dir`: Output directory (default: `loxi_output`)
- `--lang`: Target language (c, python3, java, wireshark)
- `--version-list`: Comma-separated OpenFlow versions to generate (C only)

## Important Global State

- `loxi_globals.py`: Contains `OFVersions` registry and global `ir` OrderedDict
- `ir` dictionary: Maps `OFVersion` → `OFProtocol` for each version
- Built incrementally during code generation pipeline
- Timestamp files `.loxi_ts.*` track regeneration needs (deleted by `make clean`)

## Key Utilities

- `generic_utils.py`: General-purpose utilities for code generation
- `loxi_utils/loxi_utils.py`: LOXI-specific utility functions
- `template_utils.py`: Template rendering helper functions
- `pyparsing.py`: Third-party parsing library (vendored)
- `tenjin.py`: Third-party templating engine (vendored)
