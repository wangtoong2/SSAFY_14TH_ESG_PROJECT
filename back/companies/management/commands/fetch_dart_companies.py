import io
import os
import zipfile
import xml.etree.ElementTree as ET

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from companies.models import Company


class Command(BaseCommand):
    help = 'Fetch full company list (corpCode) from DART Open API and save to DB.'

    def add_arguments(self, parser):
        parser.add_argument('--api-key', dest='api_key', help='DART API key (overrides settings.DART_API_KEY)')

    def handle(self, *args, **options):
        api_key = options.get('api_key') or getattr(settings, 'DART_API_KEY', None) or os.environ.get('DART_API_KEY')
        if not api_key:
            self.stderr.write('DART API key not provided. Set settings.DART_API_KEY or pass --api-key or set env DART_API_KEY')
            return

        url = f'https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}'
        self.stdout.write('Requesting DART corpCode zip...')
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
        except Exception as e:
            self.stderr.write(f'Error fetching corpCode: {e}')
            return

        # The API returns a ZIP containing an XML file. Read it in memory.
        try:
            z = zipfile.ZipFile(io.BytesIO(resp.content))
        except Exception:
            self.stderr.write('Response is not a valid zip archive.')
            return

        xml_name = None
        for name in z.namelist():
            if name.lower().endswith('.xml'):
                xml_name = name
                break

        if not xml_name:
            self.stderr.write('No XML file found in the zip archive.')
            return

        xml_bytes = z.read(xml_name)

        try:
            root = ET.fromstring(xml_bytes)
        except Exception as e:
            self.stderr.write(f'Failed to parse XML: {e}')
            return

        # Parse list entries and save/update Company records
        lists = root.findall('.//list')
        total = 0
        updated = 0
        created = 0
        for item in lists:
            corp_code = item.findtext('corp_code') or item.findtext('corpCode')
            corp_name = item.findtext('corp_name') or item.findtext('corpName')
            stock_code = item.findtext('stock_code') or item.findtext('stockCode')

            if not corp_code or not corp_name:
                continue

            total += 1
            obj, was_created = Company.objects.update_or_create(
                corp_code=corp_code,
                defaults={'corp_name': corp_name, 'stock_code': stock_code or None},
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Processed {total} entries: created={created}, updated={updated}'))
