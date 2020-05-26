import sys
import logging
from os import path
import re

import click
from watchdog.observers import Observer
from watchdog.events import DirCreatedEvent, FileCreatedEvent

from sharpei import __version__
from .handler import SharpeiEventHandler


_s3_path_re = re.compile(r"s3://(.+?)/(.+)?$")


@click.command()
@click.argument('local')
@click.argument('remote')
@click.option('--init', '--initial-sync', 'initial_sync', is_flag=True)
def sharpei(
    local: str,
    remote: str,
    initial_sync: bool,
):
    """
    Sync LOCAL to REMOTE

    LOCAL is a local file or directory
    REMOTE is an s3 target of format s3://bucket/[key / key prefix]
    """
    local = path.abspath(local)
    click.echo(click.style("Sharpei", fg="cyan", bold=True) + f" {__version__} watching {local} for changes")

    # Break up s3 string
    match = re.fullmatch(_s3_path_re, remote)
    if not match:
        raise click.ClickException("Invalid remote path or prefix, must be of format s3://bucket/[path]")
    s3_bucket, s3_prefix = match.groups()

    event_handler = SharpeiEventHandler(
        base_path=local,
        bucket=s3_bucket,
        base_key=s3_prefix or "",
        s3_args={},  # TODO
    )

    if initial_sync:
        if path.isfile(local):
            initial_sync_event = FileCreatedEvent(local)
        else:
            initial_sync_event = DirCreatedEvent(local)
        initial_sync_event.is_synthetic = True
        event_handler.on_created(initial_sync_event)

    observer = Observer()
    observer.schedule(event_handler, local, recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        click.echo(f"Sharpei exiting.")
        observer.stop()
    observer.join()


def main():
    logging.basicConfig(level=logging.INFO)
    sharpei(sys.argv[1:])


if __name__ == "__main__":
    main()
