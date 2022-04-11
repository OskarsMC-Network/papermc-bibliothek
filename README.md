# papermc-bibliothek

pythonic [bibliothek](https://github.com/PaperMC/bibliothek) API wrapper with a CLI

## Installation

papermc-bibliothek requires python 3.9 or above

```shell
# PIP3
pip3 install papermc-bibliothek
# PIP
pip install papermc-bibliothek
```

## API

All functions and classes are properly type hinted and documented with triple quotes. Please file an issue or pull
request with any corrections if any issues are found.

### Basic Usage

```python
from bibliothek.bibliothek import Bibliothek, BibliothekException

bibliothek = Bibliothek()  # Create an instance of the Bibliothek class
try:
    projects = bibliothek.get_projects()
    print(projects)  # ['paper', 'travertine', 'waterfall', 'velocity']
except BibliothekException as e:  # Catch BibliothekException in case something goes wrong
    print(f"Error: {e}")
```

## CLI

Will generally contain most features of the API<!--, use (the secret project) for proper server managment-->.

```shell
Usage: bibliothek [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  download-build
  get-build
  get-project
  get-projects
  get-version
  get-version-group
  get-version-group-builds
```