from collections.abc import Generator
from contextlib import contextmanager

from django.db.transaction import atomic


class DoRollback(Exception):
    pass


@contextmanager
def rollback_atomic() -> Generator[None, None, None]:
    try:
        with atomic():
            yield
            raise DoRollback()
    except DoRollback:
        pass


def get_atomic_context(dryrun=False):
    return rollback_atomic() if dryrun else atomic()
