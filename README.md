# 👷‍♀️ PyMender

Perform entire codebase refactors in a way that is _reproducible_, _testable_ and _reviewable_. Obeys `.gitignore` by default.

## Usage

```bash
pip install pymender==0.2.0

pymender <codemod> <path_to_project>
```

## What codemods are available?

### ⚡ `FastAPIAnnotated`

Converts FastAPI endpoints to use the preferred `Annotated[<type>, Depends(<dependency>)]` syntax rather than `: <type> = Depends(<dependency>)`.

**Why?**

- *Default* value of the function parameter is the *actual default* value.
- *Reuse* of the function is now possible.
- *Type-safe* usage of the functions, previously 'default' values where not type checked.
- *Multi-purpose* e.g. `Annotated[str, fastapi.Query(), typer.Argument()]` is now possible.

```bash
pymender FastAPIAnnotated <folder-to-upgrade>
```

| Before | After |
| --- | --- |
| <pre>@router.get('/example')<br/>def example_function(<br/>    value: int,<br/>    query: str = Query("foo"),<br/>    zar: str = Query(default="bar", alias="z"),<br/>    foo: str = Depends(get_foo),<br/>    *,<br/>    bar: str = Depends(get_bar),<br/>    body: str = Body(...),<br/>) -> str:<br/>    return 'example'</pre> | <pre>@router.get('/example')<br/>def example_function(<br/>    value: int,<br/>    foo: Annotated[str, Depends(get_foo)],<br/>    query: Annotated[str, Query()] = "foo",<br/>    zar: Annotated[str, Query(alias="z")] = "bar",<br/>    *,<br/>    bar: Annotated[str, Depends(get_bar)],<br/>    body: Annotated[str, Body()],<br/>) -> str:<br/>    return 'example'</pre> |

### `MovePackage`

Moves a package from one location to another.

```bash
pymender MovePackage --from <from> --to <to> <path_to_project>
```
```

## Developer Guide

```bash
# Run a particular codemod
python3 -m pymender <codemod> <path_to_project>
# e.g.
python3 -m pymender FastAPIAnnotated <path_to_project>

# Run the codemod directly
python3 -m libcst.tool codemode fastapi_annotated.FastAPIAnnotated <path_to_project>

# Run tests
pytest -vv

```

## Thanks to:

- [libCST](https://github.com/Instagram/LibCST) which does a lot of the hardwork for this.
- [autotyping](https://github.com/JelleZijlstra/autotyping) for showing what was possible.
