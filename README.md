# PyMender

Uses the excellent [libCST](https://github.com/Instagram/LibCST) to perform entire codebase refactors.

## Usage

```bash
pip install pymender==0.0.3


# Run a particular codemod
python3 -m pymender <codemod> <path_to_project>
# e.g.
python3 -m pymender FastAPIAnnotated <path_to_project>

```

## Developer

```bash

# Run the codemod directly
python3 -m libcst.tool codemode fastapi_annotated.FastAPIAnnotated <path_to_project>


# Run tests
pytest -vv

```
