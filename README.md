# importopoi

[![Documentation](https://readthedocs.org/projects/importopoi/badge/?version=latest)](https://importopoi.readthedocs.io/en/latest/)
[![CI Status](https://github.com/lmmx/importopoi/actions/workflows/master.yml/badge.svg)](https://github.com/lmmx/importopoi/actions/workflows/master.yml)
[![Coverage](https://codecov.io/gh/lmmx/importopoi/branch/master/graph/badge.svg)](https://codecov.io/github/lmmx/importopoi)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Visualising module connections within a Python package

[Read The Docs](https://importopoi.readthedocs.io/en/latest/) here and the [blog series][blog-post] I
wrote while developing it.

[blog-post]: https://pore.spin.systems/importopoi

## Plan

- Use `impgraph`'s JSON output to get an import graph in JSON, running the following in
  `subprocess.run` for now and later simplifying to use the Python internals

  ```sh
  impgraph src/importopoi/ -j /dev/stdout
  ```

- Use `import_dep`'s

## Requires

- Python 3.9+

## Installation

```sh
pip install importopoi
```

> _importopoi_ is available from [PyPI](https://pypi.org/project/importopoi), and
> the code is on [GitHub](https://github.com/lmmx/importopoi)
