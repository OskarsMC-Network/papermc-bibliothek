# papermc-bibliothek

pythonic [bibliothek](https://github.com/PaperMC/bibliothek) API wrapper

## Installation

papermc-bibliothek requires python 3.9 or above

```shell
pip install papermc-bibliothek
```

```shell
poetry add papermc-bibliothek
```

## API

All functions and classes are properly type hinted and documented with triple quotes. Please file an issue or pull
request with any corrections if any issues are found.

You can refer to https://papermc.io/api if looking for a specific
method, they are named similarly.

### Basic Usage

```python
from bibliothek import Bibliothek, BibliothekException

bibliothek = Bibliothek()  # Create an instance of the Bibliothek class
try:
    projects = bibliothek.get_projects()
    print(projects)  # ['paper', 'travertine', 'waterfall', 'velocity']
except BibliothekException as e:  # Catch BibliothekException in case something goes wrong
    print(f"Error: {e}")
```