"""
cli implementaion for package:
    exposes:
        get_db_path() via example()
"""
import sys
import click
from .voice_memos_printer import VoiceMemosPrinter
from .voicememo_db import cli_get_db_path
from .memo_data import get_memo_data

def _get_db():
    db_path = cli_get_db_path()
    if not db_path[0]:
        print(f"{db_path[1]}")
        sys.exit(1)
    else:
        return str(db_path[1])

@click.group
def main():
    pass

@main.command
def example():
    db_path = _get_db()
    VoiceMemosPrinter.example_usage_patterns(db_path)

@main.command
def filetree():
    db_path = _get_db()
    records = get_memo_data(db_path)
    VoiceMemosPrinter.print_memo_files(records)



