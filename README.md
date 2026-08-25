# paneltime_mp

Author: Espen Sirnes
Version: 0.0.2

Multiprocessing interface

## Setup

Use the setup helper script from the project root:

```bash
python setup_script.py
```

This cleans old build artifacts and installs the package in editable mode (`pip install -e .`).

Show script help:

```bash
python setup_script.py --help
```

Publish workflow (version bump, git commit/push, build, upload):

```bash
python setup_script.py -p
```

## Example Workflow

The intended flow is:

1. Start `Master(n)` with one process per worker.
2. Send one shared dictionary to all workers with `send_dict(...)`.
3. Put everything task strings need inside that dictionary, including functions.
4. Run one task string per worker using `run(tasks, "eval")` or `run(tasks, "exec")`.
5. Collect outputs with `collect()`.

```python
import operator
from paneltime_mp import Master

master = Master(2)
try:
    payload = {
        "values": [1, 2, 3],
        "factor": 5,
        "mul": operator.mul,
    }
    master.send_dict(payload)
    master.collect()

    tasks = [
        "{'node': 0, 'scaled': [mul(v, factor + 0) for v in values]}",
        "{'node': 1, 'scaled': [mul(v, factor + 1) for v in values]}",
    ]

    master.run(tasks, "eval")
    result = master.collect()
    print(result)
finally:
    master.quit()
```

## Smoke Test

Run the end-to-end smoke test:

```bash
python tests/smoke_mp.py
```
