#!/usr/bin/env python3

import json
from separation import run_analytics_pipeline

if __name__ == "__main__":
    print("Running analytics pipeline...")
    results = run_analytics_pipeline()
    print(json.dumps(results, indent=2))
