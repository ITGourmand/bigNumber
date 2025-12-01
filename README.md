# bigNumber

**bigNumber** is a Python library for working with **extremely large or small numbers**. It allows arithmetic operations on numbers with custom suffixes for huge scales (like `k`, `M`, `B`, `T`, etc.) and automatically handles normalization, comparison, and complex calculations.  

The complexity of operations depends on the difference in scale between the numbers.

## Features

- Supports **arbitrarily large or small numbers** using suffixes and blocks.
- Handles arithmetic operations: `+`, `-`, `*`, `/`, `**`.
- Normalizes numbers internally to maintain precision across huge scales.
- Provides **compact** and **non-compact** string representations.
- Can parse expressions like `2Oc/3` and output readable results.

## Installation

Not yet on PyPI. Clone the repository and import the class:

```python
from bigNumber import bigNumber
```

# Usage
```
from bigNumber import bigNumber

# Create bigNumber instances
a = bigNumber("2Oc")
b = bigNumber("3")

# Arithmetic operations
c = a / b
d = a * 5
e = b ** 10

# String representations
print(c)               # Non-compact: 666.666666666666666666666666Sp
print(bigNumber(c, compact=True))  # Compact: 666Sp+666Sx+666Qt+666Qa+666T+666B+666M+666k+666
```

# Suffixes

Predefined suffixes include:
```
"", "k", "M", "B", "T", "Qa", "Qt", "Sx", "Sp", "Oc", "No"
```
