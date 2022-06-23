""" This custom management command will import all the LGAs
    and postcodes (and their relationships) from a .csv file.

    The csv file must simply have two fields LGA and Postcode

    Usage:

    Locally with an active poetry environment:

        ./manage.sh import_lgas_postcodes_data

    Without poetry:

        ./manage.py import_lgas_postcodes_data
"""
import csv

from django.core.management.base import BaseCommand, CommandError

from parkpasses.components.parks.models import LGA, Postcode


class Command(BaseCommand):
    help = "Imports LGAs and Postcodes and their relationships from a .csv file"

    def add_arguments(self, parser):
        parser.add_argument("path_to_cvs_file", nargs="+", type=str)

    def handle(self, *args, **options):
        path_to_cvs_file = options["path_to_cvs_file"][0]
        self.stdout.write("path_to_cvs_file = %s" % path_to_cvs_file)

        try:
            open(path_to_cvs_file)
        except ValueError:
            raise CommandError(f"No import file exists at {path_to_cvs_file}.")

        records_processed = 0

        with open(path_to_cvs_file) as csvfile:
            datareader = csv.DictReader(csvfile)
            for row in datareader:
                self.stdout.write(
                    self.style.SUCCESS("{} {}".format(row["lga"], row["postcode"]))
                )
                lga, lga_created = LGA.objects.get_or_create(name=row["lga"])
                postcode, postcode_created = Postcode.objects.get_or_create(
                    postcode=row["postcode"]
                )
                lga.postcodes.add(postcode)
                records_processed += 1

        self.stdout.write(
            self.style.SUCCESS(f"Finished processing {records_processed} records.")
        )
