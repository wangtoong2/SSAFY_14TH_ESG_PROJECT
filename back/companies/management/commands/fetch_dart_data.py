from django.core.management.base import BaseCommand
from companies.services import fetch_all_companies_to_file


class Command(BaseCommand):
    help = 'Fetch DART summary data for all Company rows and save to JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('--out', type=str, default='companies_dart_cache.json')
        parser.add_argument('--save-db', action='store_true', dest='save_db', help='Save results into CompanyProfile JSONField')

    def handle(self, *args, **options):
        out = options.get('out')
        save_db = options.get('save_db')
        path = fetch_all_companies_to_file(output_path=out)
        self.stdout.write(self.style.SUCCESS(f'Wrote DART data to {path}'))
        if save_db:
            self.stdout.write(self.style.NOTICE('Saved per-company cache to DB (CompanyProfile).'))
