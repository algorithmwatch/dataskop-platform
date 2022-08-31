from django.db import models

from dataskop.utils.list import chunks

TODO_CHUNK_SIZE = 1000


class LookupJobManager(models.Manager):
    def create_chunked_todo(self, input_todo, log, **kwargs):
        for i, c in enumerate(chunks(input_todo, TODO_CHUNK_SIZE)):
            # Only append to log if the data is large enough for chunks
            fixed_log = log
            if len(input_todo) > TODO_CHUNK_SIZE:
                fixed_log += f" - chunk #{i}"

            self.create(input_todo=c, log=fixed_log, **kwargs)
