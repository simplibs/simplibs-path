# 🎲 Standalone & Type-Aware Randomizers Reference

A detailed overview of all built-in random value generators (randomizers) available in
the `simplibs.randomize` package. All functions listed below can be imported directly
from the main package:

```python
from simplibs.randomize import randomize_int, randomize_str, randomize_list ...
```
All functions are designed to be usable purely without any parameters - meaning every
one of them has default values that still produce a result even when called directly.
The text below therefore serves not only as an overview of the available options, but
also as a peek under the hood at how each function is built, and which parameters can
additionally be configured.
---

## 🧭 Table of Contents

### 1. Standalone Randomizers
Generators for standalone data types that do not require any additional type structure
(type arguments). 1.1 Primitives (Basic types)
* [`randomize_bool`](#randomize_bool)
* [`randomize_bytes`](#randomize_bytes)
* [`randomize_decimal`](#randomize_decimal)
* [`randomize_float`](#randomize_float)
* [`randomize_int`](#randomize_int)
* [`randomize_str`](#randomize_str)

1.2 Special (Special types)
* [`randomize_path`](#randomize_path)
* [`randomize_uuid`](#randomize_uuid)

1.3 Temporal (Date and time types)
* [`randomize_date`](#randomize_date)
* [`randomize_datetime`](#randomize_datetime)
* [`randomize_time`](#randomize_time)
* [`randomize_timedelta`](#randomize_timedelta)


### 2. Type-Aware Randomizers
Generators that analyze and process the internal structure of generic types. 2.1
Collections
* [`randomize_dict`](#randomize_dict)
* [`randomize_list`](#randomize_list)
* [`randomize_set`](#randomize_set)
* [`randomize_tuple`](#randomize_tuple)

2.2 Structural (Structural type hints)
* [`randomize_enum`](#randomize_enum)
* [`randomize_literal`](#randomize_literal)
* [`randomize_union`](#randomize_union)


### 3. Meta Types
Generators for special Python system meta-types and the value `None`.
* [`randomize_any`](#randomize_any)
* [`get_none`](#get_none)

---

## 1.1 Primitives (Basic types)

### `randomize_bool`

Generates a random boolean value.

**Parameters:**
* `true_probability` (*float*, optional): Probability of returning `True` (0.0 to 1.0).
  Defaults to `0.5`.

**Returns:**
* `bool`: Random `True` or `False`.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_bool

# Generate with 80% chance of True
is_active = randomize_bool(true_probability=0.8)
```

**Under the hood** (code simplified, without validation logic):
```python
import random

def randomize_bool(
    *,
    true_probability: float = 0.5
) -> bool:

    return random.random() < true_probability
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_bytes`

Generates a random sequence of bytes.

**Parameters:**
* `min_length` (*int*, optional): Minimum length in bytes. Defaults to `5`.
* `max_length` (*int*, optional): Maximum length in bytes. Defaults to `15`.

**Returns:**
* `bytes`: Random bytes object with a length between `min_length` and `max_length`.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_bytes

token = randomize_bytes(min_length=10, max_length=20)
```

**Under the hood** (code simplified, without validation logic):
```python
import random

def randomize_bytes(
    *,
    min_length: int = 5,
    max_length: int = 15
) -> bytes:

    length = random.randint(min_length, max_length)
    return random.randbytes(length)
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_decimal`

Generates a random Decimal value.

**Parameters:**
* `min_value` (*float*, optional): Lower bound of the generated value. Defaults to
  `0.0`.
* `max_value` (*float*, optional): Upper bound of the generated value. Defaults to
  `1000.0`.
* `exponent` (*int*, optional): Decimal precision exponent (e.g., -2 for hundredths).
  Must be non-positive. Defaults to `-2`.

**Returns:**
* `Decimal`: Random Decimal value quantized to the specified exponent.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_decimal

price = randomize_decimal(min_value=1.99, max_value=99.99, exponent=-2)
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from decimal import Decimal

def randomize_decimal(
    *,
    min_value: float = 0.0,
    max_value: float = 1000.0,
    exponent: int = -2,
) -> Decimal:

    value = random.uniform(float(min_value), float(max_value))
    target_precision = Decimal(f"1e{exponent}")
    
    return Decimal(str(value)).quantize(target_precision)
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_float`

Generates a random floating-point number within a specified range.

**Parameters:**
* `min_value` (*float*, optional): Lower bound of the generated value. Defaults to
  `0.0`.
* `max_value` (*float*, optional): Upper bound of the generated value. Defaults to
  `1000.0`.
* `ndigits` (*int*, optional): Number of decimal places to round to. Defaults to `2`.

**Returns:**
* `float`: Random float rounded to `ndigits` decimal places.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_float

temperature = randomize_float(min_value=-10.0, max_value=40.0, ndigits=1)
```

**Under the hood** (code simplified, without validation logic):
```python
import random

def randomize_float(
    *,
    min_value: float = 0.0,
    max_value: float = 1000.0,
    ndigits: int = 2,
) -> float:

    return round(random.uniform(float(min_value), float(max_value)), ndigits)
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_int`

Generates a random integer within a specified range.

**Parameters:**
* `min_value` (*int*, optional): Lower bound (inclusive). Defaults to `0`.
* `max_value` (*int*, optional): Upper bound (inclusive). Defaults to `1000`.

**Returns:**
* `int`: Random integer from the interval [`min_value`, `max_value`].

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_int

age = randomize_int(min_value=18, max_value=65)
```

**Under the hood** (code simplified, without validation logic):
```python
import random

def randomize_int(
    *,
    min_value: int = 0,
    max_value: int = 1000
) -> int:

    return random.randint(min_value, max_value)
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_str`

Generates a random text string.

**Parameters:**
* `min_length` (*int*, optional): Minimum string length. Defaults to `5`.
* `max_length` (*int*, optional): Maximum string length. Defaults to `15`.
* `alphabet` (*str*, optional): Set of characters used to build the string. Defaults to
  `ascii_letters + digits`.

**Returns:**
* `str`: Random string with length between `min_length` and `max_length`.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_str

username = randomize_str(min_length=8, max_length=12, alphabet="abcdefghijklmnopqrstuvwxyz")
```

**Under the hood** (code simplified, without validation logic):
```python
import random
import string

def randomize_str(
    *,
    min_length: int = 5,
    max_length: int = 15,
    alphabet: str = string.ascii_letters + string.digits,
) -> str:

    length = random.randint(min_length, max_length)
    return "".join(random.choices(alphabet, k=length))
```

[▲ Back to top](#-table-of-contents)


---

## 1.2 Special (Special types)

### `randomize_path`

Generates a random file path (the file does not need to exist).

**Parameters:**
* `directory` (*str | Path*, optional): Directory where the path should reside. Defaults
  to `"/tmp"`.
* `extension` (*str*, optional): File extension (including leading dot). Defaults to
  `".txt"`.
* `name_length` (*int*, optional): Length of the randomly generated base filename.
  Defaults to `10`.

**Returns:**
* `Path`: Path object composed of `directory / random_name + extension`.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_path

file_path = randomize_path(directory="/var/log", extension=".csv", name_length=8)
```

**Under the hood** (code simplified, without validation logic):
```python
import random
import string
from pathlib import Path

def randomize_path(
    *,
    directory: str = "/tmp",
    extension: str = ".txt",
    name_length: int = 10,
) -> Path:

    name = "".join(random.choices(string.ascii_lowercase, k=name_length))
    return Path(directory) / f"{name}{extension}"
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_uuid`

Generates a random UUID.

**Parameters:**
* (Operates without parameters.)

**Returns:**
* `uuid.UUID`: Random UUID object.

**Example call:**
```python
from simplibs.randomize import randomize_uuid

unique_id = randomize_uuid()
```

**Under the hood** (code simplified, without validation logic):
```python
import uuid

def randomize_uuid() -> uuid.UUID:

    return uuid.uuid4()
```

[▲ Back to top](#-table-of-contents)


---

## 1.3 Temporal (Date and time types)

### `randomize_date`

Generates a random calendar date within a specified range.

**Parameters:**
* `start` (*date*, optional): Earliest allowable date (inclusive). Defaults to
  `date(2020, 1, 1)`.
* `end` (*date*, optional): Latest allowable date (inclusive). Defaults to `date(2025,
  12, 31)`.

**Returns:**
* `date`: Random date object from the interval [`start`, `end`].

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from datetime import date
from simplibs.randomize import randomize_date

event_date = randomize_date(start=date(2026, 1, 1), end=date(2026, 12, 31))
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from datetime import date, timedelta

def randomize_date(
    *,
    start: date = date(2020, 1, 1),
    end: date = date(2025, 12, 31),
) -> date:

    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_datetime`

Generates a random datetime within a specified range.

**Parameters:**
* `start` (*datetime*, optional): Earliest allowable timestamp (inclusive). Defaults to
  `datetime(2020, 1, 1)`.
* `end` (*datetime*, optional): Latest allowable timestamp (inclusive). Defaults to
  `datetime(2025, 12, 31)`.

**Returns:**
* `datetime`: Random datetime object from the interval [`start`, `end`].

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from datetime import datetime
from simplibs.randomize import randomize_datetime

created_at = randomize_datetime(start=datetime(2026, 1, 1), end=datetime(2026, 6, 30))
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from datetime import datetime, timedelta

def randomize_datetime(
    *,
    start: datetime = datetime(2020, 1, 1),
    end: datetime = datetime(2025, 12, 31),
) -> datetime:

    total_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, total_seconds))
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_time`

Generates a random time of day (independent of date).

**Parameters:**
* `min_hour` (*int*, optional): Minimum allowable hour (0 to 23). Defaults to `0`.
* `max_hour` (*int*, optional): Maximum allowable hour (0 to 23). Defaults to `23`.

**Returns:**
* `time`: Random time object with hours, minutes, and seconds.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_time

work_start = randomize_time(min_hour=6, max_hour=9)
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from datetime import time

def randomize_time(
    *,
    min_hour: int = 0,
    max_hour: int = 23,
) -> time:

    hour = random.randint(min_hour, max_hour)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    return time(hour=hour, minute=minute, second=second)
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_timedelta`

Generates a random time duration/interval.

**Parameters:**
* `min_seconds` (*int*, optional): Minimum duration in seconds. Defaults to `0`.
* `max_seconds` (*int*, optional): Maximum duration in seconds. Defaults to `2592000`
  (30 days).

**Returns:**
* `timedelta`: Random timedelta instance between `min_seconds` and `max_seconds`.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_timedelta

delay = randomize_timedelta(min_seconds=60, max_seconds=3600)
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from datetime import timedelta

def randomize_timedelta(
    *,
    min_seconds: int = 0,
    max_seconds: int = 60 * 60 * 24 * 30,
) -> timedelta:

    seconds = random.randint(min_seconds, max_seconds)
    return timedelta(seconds=seconds)
```

[▲ Back to top](#-table-of-contents)


---

## 2.1 Collections

### `randomize_dict`

Generates a random dictionary based on a parameterized dictionary type hint.

**Parameters:**
* `dict_type` (*Any*, optional): Parameterized dict type hint (e.g., `dict[str, int]` or
  `dict[int, float]`). If bare `dict` is passed, defaults to `dict[str, str]`. Defaults
  to `dict`.
* `min_length` (*int*, optional): Minimum allowable number of key-value pairs in the
  generated dictionary. Defaults to `1`.
* `max_length` (*int*, optional): Maximum allowable number of key-value pairs in the
  generated dictionary. Defaults to `5`.

**Returns:**
* `dict[Any, Any]`: Dictionary populated with randomly generated key-value pairs
  matching specified types.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_dict

mapping = randomize_dict(dict_type=dict[str, int], min_length=2, max_length=4)
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from typing import Any, get_origin, get_args
from simplibs.randomize.tools.decorator import value_type_name
from simplibs.randomize.get_randomizer import get_randomizer

@value_type_name("dict_type")
def randomize_dict(
    dict_type: Any = dict,
    *,
    min_length: int = 1,
    max_length: int = 5,
) -> dict[Any, Any]:

    _dict_type = dict[str, str] if dict_type is dict else dict_type

    key_type, value_type = get_args(_dict_type)
    key_randomize = get_randomizer(key_type)
    value_randomize = get_randomizer(value_type)
    
    length = random.randint(min_length, max_length)

    return {
        key_randomize(): value_randomize()
        for _ in range(length)
    }
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_list`

Generates a random list based on a parameterized list type hint.

**Parameters:**
* `list_type` (*Any*, optional): Parameterized list type hint (e.g., `list[int]` or
  `list[str]`). If bare `list` is passed, defaults to `list[str]`. Defaults to `list`.
* `min_length` (*int*, optional): Minimum allowable number of items in the generated
  list. Defaults to `1`.
* `max_length` (*int*, optional): Maximum allowable number of items in the generated
  list. Defaults to `5`.

**Returns:**
* `list[Any]`: List populated with randomly generated items matching the specified type.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_list

numbers = randomize_list(list_type=list[int], min_length=3, max_length=10)
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from typing import Any, get_origin, get_args
from simplibs.randomize.tools.decorator import value_type_name
from simplibs.randomize.get_randomizer import get_randomizer

@value_type_name("list_type")
def randomize_list(
    list_type: Any = list,
    *,
    min_length: int = 1,
    max_length: int = 5,
) -> list[Any]:

    _list_type = list[str] if list_type is list else list_type

    (item_type,) = get_args(_list_type)
    item_randomize = get_randomizer(item_type)
    length = random.randint(min_length, max_length)

    return [
        item_randomize()
        for _ in range(length)
    ]
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_set`

Generates a random set based on a parameterized set type hint.

**Parameters:**
* `set_type` (*Any*, optional): Parameterized set type hint (e.g., `set[int]` or
  `set[str]`). If bare `set` is passed, defaults to `set[str]`. Defaults to `set[str]`.
* `min_length` (*int*, optional): Minimum allowable number of unique items in the
  generated set. Defaults to `1`.
* `max_length` (*int*, optional): Maximum allowable number of unique items in the
  generated set. Defaults to `5`.
* `max_attempts` (*int*, optional): Maximum insertion attempts to fulfill target length
  when duplicate values are generated. Defaults to `50`.

**Returns:**
* `set[Any]`: Set populated with randomly generated unique items matching the specified
  type.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_set

tags = randomize_set(set_type=set[str], min_length=2, max_length=5)
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from typing import Any, get_origin, get_args
from simplibs.randomize.tools.decorator import value_type_name
from simplibs.randomize.get_randomizer import get_randomizer

@value_type_name("set_type")
def randomize_set(
    set_type: Any = set[str],
    *,
    min_length: int = 1,
    max_length: int = 5,
    max_attempts: int = 50,
) -> set[Any]:

    _set_type = set[str] if set_type is set else set_type

    (item_type,) = get_args(_set_type)
    item_randomize = get_randomizer(item_type)
    target_length = random.randint(min_length, max_length)
    
    result: set[Any] = set()
    attempts = 0
    while len(result) < target_length and attempts < max_attempts:
        result.add(item_randomize())
        attempts += 1

    return result
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_tuple`

Generates a random tuple based on a parameterized tuple type hint.

**Parameters:**
* `tuple_type` (*Any*, optional): Parameterized tuple type hint (e.g., `tuple[int, ...]`
  or `tuple[str, int]`). If bare `tuple` is passed, defaults to `tuple[str, ...]`.
  Defaults to `tuple`.
* `min_length` (*int*, optional): Minimum allowable number of items in the generated
  tuple. Defaults to `1`.
* `max_length` (*int*, optional): Maximum allowable number of items in the generated
  tuple. Defaults to `5`.

**Returns:**
* `tuple[Any, ...]`: Tuple populated with randomly generated items matching the
  specified type.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_tuple

point = randomize_tuple(tuple_type=tuple[int, int, int])
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from typing import Any, get_origin, get_args
from simplibs.randomize.tools.decorator import value_type_name
from simplibs.randomize.get_randomizer import get_randomizer

@value_type_name("tuple_type")
def randomize_tuple(
    tuple_type: Any = tuple,
    *,
    min_length: int = 1,
    max_length: int = 5,
) -> tuple[Any, ...]:

    _tuple_type = tuple[str, ...] if tuple_type is tuple else tuple_type

    args = get_args(_tuple_type)
    item_type = args[0]
    item_randomize = get_randomizer(item_type)
    length = random.randint(min_length, max_length)

    return tuple(
        item_randomize()
        for _ in range(length)
    )

```

[▲ Back to top](#-table-of-contents)


---

## 2.2 Structural (Structural type hints)

### `randomize_enum`

Generates a random Enum member from a provided Enum class.

**Parameters:**
* `enum_type` (*type[Enum]*, optional): Enum class from which a member is selected.
  Defaults to `Enum`.
* `exclude` (*Iterable[Enum] | None*, optional): Optional iterable of specific Enum
  members to exclude from selection. Defaults to `None`.

**Returns:**
* `Enum | None`: Randomly selected Enum member, or `None` if an unparameterized base
  Enum is provided.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from enum import Enum
from simplibs.randomize import randomize_enum

class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

status = randomize_enum(enum_type=Status, exclude=[Status.REJECTED])
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from typing import Any
from collections.abc import Iterable
from enum import Enum, EnumType
from simplibs.randomize.tools.decorator import value_type_name
from simplibs.randomize.get_randomizer import get_randomizer

@value_type_name("enum_type")
def randomize_enum(
    enum_type: type[Enum] = Enum,
    *,
    exclude: Iterable[Enum] | None = None,
) -> Enum | None:

    if enum_type in (Enum, EnumType, Any):
        return None

    excluded = set(exclude or ())
    candidates = [item for item in enum_type if item not in excluded]
    
    return random.choice(candidates)
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_literal`

Generates a random value based on a parameterized Literal type hint.

**Parameters:**
* `literal_type` (*Any*, optional): Parameterized Literal type hint (e.g.,
  `Literal["red", "green", "blue"]` or `Literal[1, 2, 3]`). Defaults to `Literal`.

**Returns:**
* `Any`: Randomly selected literal value from the specified choices.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from typing import Literal
from simplibs.randomize import randomize_literal

color = randomize_literal(literal_type=Literal["red", "green", "blue"])
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from typing import Any, get_origin, get_args, Literal
from simplibs.randomize.tools.decorator import value_type_name
from simplibs.randomize.get_randomizer import get_randomizer

@value_type_name("literal_type")
def randomize_literal(
    literal_type: Any = Literal,
) -> Any:

    if literal_type in (Literal, Any):
        return None

    allowed_values = get_args(literal_type)
    
    return random.choice(allowed_values)
```

[▲ Back to top](#-table-of-contents)


---

### `randomize_union`

Generates a random value based on a Union type hint (e.g., `Union[int, str]` or `int |
str | None`).

**Parameters:**
* `union_type` (*Any*, optional): Union type hint (`Union[...]` or `A | B` syntax).
  Defaults to `UnionType`.
* `none_probability` (*float*, optional): Probability of returning `None` when `None` /
  `type(None)` is included in the Union variants. Must be between 0.0 and 1.0. Defaults
  to `0.3`.

**Returns:**
* `Any`: Randomly generated value matching one of the union variants, or `None`.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from typing import Union
from simplibs.randomize import randomize_union

val = randomize_union(union_type=Union[int, str, None], none_probability=0.1)
```

**Under the hood** (code simplified, without validation logic):
```python
import random
from typing import Any, get_origin, get_args, Union
from types import UnionType
from simplibs.randomize.tools.decorator import value_type_name
from simplibs.randomize.get_randomizer import get_randomizer

@value_type_name("union_type")
def randomize_union(
    union_type: Any = UnionType,
    *,
    none_probability: float = 0.3,
) -> Any:

    if union_type in (UnionType, Union, Any):
        return None

    args = get_args(union_type)
    has_none = type(None) in args
    generators = [
        get_randomizer(item_type)
        for item_type in args
        if item_type is not type(None)
    ]
    
    if has_none and random.random() < none_probability:
        return None
    
    generator = random.choice(generators)
    return generator()
```

[▲ Back to top](#-table-of-contents)


---

## 3. Meta Types

### `randomize_any`

Generates a random value for the Any meta-type from candidate types or values.

If no choices are provided, defaults to generating a string value.

**Parameters:**
* `*choices` (*Any*): Candidate data types or values to randomly choose from.
* `validate` (*bool*, optional): Whether to validate the presence of provided types
  within the global registry. Set to `False` when supplying local non-registered types
  or specific instances. Defaults to `True`.

**Returns:**
* `Any`: Randomly generated value based on one of the selected choices.

**Example of a parametrized call** (the function can also be called without any
parameters):
```python
from simplibs.randomize import randomize_any

# Pick randomly from candidate types and generate a value
any_val = randomize_any(int, str, bool)
```

**Under the hood** (code simplified, without validation logic):
```python
from random import choice
from typing import Any
from simplibs.randomize.get_randomizer import get_randomizer

def randomize_any(
    *choices: Any,
) -> Any:
        
    selected_type = choice(choices) if choices else str
    randomize = get_randomizer(selected_type)
    
    return randomize()
```

[▲ Back to top](#-table-of-contents)


---

### `get_none`

Returns None type.

**Returns:**
* `None`: Always returns `None`.

**Example call:**
```python
from simplibs.randomize import get_none

empty_value = get_none() # -> None
```

**Under the hood** (code simplified, without validation logic):
```python
def get_none() -> None:
    
    return None
```

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../_README.md)