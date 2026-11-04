"""Rebuild all public-facing research figures and tables from archived real data."""
from src.pipeline import run_all
if __name__=='__main__':
    import json
    print(json.dumps(run_all(),indent=2,ensure_ascii=False))
