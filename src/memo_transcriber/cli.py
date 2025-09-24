"""
cli implementaion for package:
    exposes:
        get_db_path() via example()
"""
import sys
from .memo_data import example_usage_patterns
from .voicememo_db import cli_get_db_path

def example():
    db_path = cli_get_db_path()
    if not db_path[0]:
        print(f"{db_path[1]}")
        sys.exit(1)
    else:
        db_path = str(db_path[1])

    example_usage_patterns(db_path)


