# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About LoxiGen

LoxiGen is a code generator that produces OpenFlow protocol libraries for multiple languages (C, Python3, Java, and Wireshark dissector). It parses wire protocol descriptions from input files and generates language-specific implementations supporting OpenFlow versions 1.0-1.5.1.

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
pytest
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
- `lang_c.py`, `lang_java.py`, `lang_python3.py`: Language-specific configuration defining what files to generate
- `loxi_globals.py`: Global state including OFVersions registry

### Template System

Each backend uses templates in `<lang>_gen/templates/`:
- Templates use Tenjin templating engine (`tenjin.py`)
- `template_utils.py`: Helper functions for template rendering

### OpenFlow Version Support

Versions defined in `loxi_globals.py` OFVersions class:
- 1.0, 1.1, 1.2, 1.3, 1.4, 1.5
- Production-ready: 1.0, 1.3.1, 1.4.1
- Experimental: 1.1, 1.2, 1.5.1 (Java only)

### Generated Output Structure

```
loxi_output/
  loci/          # C library (LOCI)
  pyloxi3/       # Python3 library
  openflowj/     # Java library (openflowj)
  wireshark/     # Wireshark dissector
```

## Input File Format

Input files in `openflow_input/` define OpenFlow protocol structures:
- Struct definitions with fields: `type field_name;`
- Lists: `list(type) field_name;`
- Arrays: `type[length] field_name;`
- Version-specific variants (e.g., match structures renamed per version)
- Extensions (BSN-specific messages and actions)

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
- Uses Maven for build and dependency management
- Package: `org.projectfloodlight.openflow.*`

## Testing Infrastructure

- `utest/`: Python unit tests for LoxiGen itself (parser, IR, etc.)
- `test_data/`: Test data files with `.data` extension used during generation
- Language-specific tests in generated output directories
- C tests: `loxi_output/locitest/`
- Python tests: `py_gen/tests3/`
- Java tests: `java_gen/pre-written/src/test/`
