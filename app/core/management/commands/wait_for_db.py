"""
Django command to wait for db to be available
"""

import time
from psycopg2 import OperationalError as PycopgError
from django.db.utils import OperationalError

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django command to wait for database
    """
    def handle(self, *args, **options):
        """ entry point to commands """

        db_up = False
        self.stdout.write("Watiting for Database")
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except(PycopgError, OperationalError):
                self.stdout.write("Database unvailable. waiting 1 sec...")
                time.sleep(1)

        self.stdout.write("Database avaialable!")
