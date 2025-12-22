from django.core.management.base import BaseCommand
from companies.models import Company, CompanyProfile
from companies.services import (
    fetch_company_data,
    fetch_financial_summary,
    fetch_company_overview,
    classify_company_size,
)
import time
import os
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Bulk fetch DART data for all companies and save into CompanyProfile (dry-run unless --confirm)'

    def add_arguments(self, parser):
        parser.add_argument('--sleep', type=float, default=0.05, help='Seconds to sleep between requests')
        parser.add_argument('--start', type=int, default=0, help='Start index (0-based)')
        parser.add_argument('--limit', type=int, default=0, help='Max companies to process (0 = all)')
        parser.add_argument('--confirm', action='store_true', help='Actually perform DB writes')

    def handle(self, *args, **options):
        sleep = options.get('sleep')
        start = options.get('start')
        limit = options.get('limit')
        confirm = options.get('confirm')

        qs = Company.objects.all().order_by('id')
        total = qs.count()
        self.stdout.write(f'Total companies: {total}')
        if limit > 0:
            total = min(total, start + limit)

        err_log = os.path.join(os.getcwd(), 'bulk_update_errors.log')
        with open(err_log, 'a', encoding='utf-8') as elog:
            processed = 0
            for idx, c in enumerate(qs[start: (start+limit) if limit>0 else None], start+1):
                try:
                    self.stdout.write(f'[{idx}/{total}] Fetching {c.corp_name} (corp_code={c.corp_code})')
                    # try using corp_code first for overview and financials
                    data = None
                    if c.corp_code:
                        try:
                            data = fetch_company_data(c.corp_code)
                        except Exception:
                            data = None
                    if not data:
                        data = fetch_company_data(c.corp_name)

                    # if still missing overview or financials, try explicit calls
                    if (not data.get('company_overview')) and c.corp_code:
                        try:
                            ov = fetch_company_overview(c.corp_code)
                            if ov:
                                data['company_overview'] = ov
                        except Exception:
                            pass
                    if (not data.get('financials')) and c.corp_code:
                        try:
                            fin = fetch_financial_summary(c.corp_code)
                            if fin:
                                data['financials'] = fin
                        except Exception:
                            pass

                    data['stock_code'] = c.stock_code
                    try:
                        data['company_size'] = classify_company_size(c.stock_code, data.get('financials'))
                    except Exception:
                        data['company_size'] = data.get('company_size')

                    if confirm:
                        try:
                            CompanyProfile.objects.update_or_create(company=c, defaults={'data': data})
                        except Exception as db_e:
                            elog.write(f'DB error for {c.corp_name}: {db_e}\n')
                            elog.flush()
                            logger.exception('DB save error for %s', c.corp_name)
                    else:
                        # dry-run: just show keys
                        self.stdout.write('Dry-run keys: ' + ','.join(data.keys()))

                    processed += 1
                except Exception as e:
                    elog.write(f'Fetch error for {c.corp_name}: {e}\n')
                    elog.flush()
                    logger.exception('Fetch error for %s', c.corp_name)
                time.sleep(sleep)

        self.stdout.write(f'Done. Processed: {processed}. Errors logged to {err_log}')