#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Basic end-to-end smoke test for paneltime_mp multiprocessing flow.

Run:
  python tests/smoke_mp.py
"""

import operator

from paneltime_mp import Master


def main():
    master = Master(2)
    try:
        payload = {
            "values": [1, 2, 3],
            "factor": 5,
            # Function object is part of the shared dict and used by task strings.
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

        if len(result) != 2:
            raise AssertionError(f"Expected results from 2 slaves, got: {result}")

        scaled_lists = sorted(item["scaled"] for item in result.values())
        expected = sorted([[5, 10, 15], [6, 12, 18]])
        if scaled_lists != expected:
            raise AssertionError(f"Unexpected eval result. expected={expected}, got={scaled_lists}")

        print("smoke test passed")
    finally:
        master.quit()


if __name__ == "__main__":
    main()
