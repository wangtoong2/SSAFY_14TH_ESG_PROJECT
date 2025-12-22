import os
import time

from django.core.management.base import BaseCommand

from companies.models import CompanyProfile
from companies.services import build_fixed_companyprofile_payload, classify_company_size


def _canonical_stock_code(v):
    if v is None:
        return None
    try:
        s = str(v).strip()
    except Exception:
        return None
    return s or None


class Command(BaseCommand):
    help = (
        "Backfill CompanyProfile.data to ensure a stable schema for key fields. "
        "Preserves existing data; only normalizes/ensures required keys exist. "
        "Dry-run by default; use --confirm to write."
    )

    def add_arguments(self, parser):
        parser.add_argument('--sleep', type=float, default=0.0, help='Seconds to sleep between DB writes')
        parser.add_argument('--start', type=int, default=0, help='Start index (0-based)')
        parser.add_argument('--limit', type=int, default=0, help='Max profiles to process (0 = all)')
        parser.add_argument('--confirm', action='store_true', help='Actually perform DB writes')
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help=(
                'Overwrite CompanyProfile.data to the fixed schema only '
                '(drops extra keys like disclosures/financials/raw unless they are part of the fixed payload).'
            ),
        )
        parser.add_argument('--log-every', type=int, default=200, help='Log progress every N profiles')

    def handle(self, *args, **options):
        sleep = float(options.get('sleep') or 0.0)
        start = int(options.get('start') or 0)
        limit = int(options.get('limit') or 0)
        confirm = bool(options.get('confirm'))
        overwrite = bool(options.get('overwrite'))
        log_every = int(options.get('log_every') or 200)

        qs = CompanyProfile.objects.select_related('company').order_by('id')
        total = qs.count()
        requested_end = (start + limit) if limit and limit > 0 else total
        end = min(requested_end, total)

        self.stdout.write(f'Total profiles: {total}')
        self.stdout.write(f'Processing range: [{start}, {requested_end}) (effective: [{start}, {end}))')
        mode = 'WRITE (--confirm)' if confirm else 'DRY-RUN'
        mode += ' + OVERWRITE' if overwrite else ' + MERGE'
        self.stdout.write('Mode: ' + mode)

        changed = 0
        processed = 0
        err_log_path = os.path.join(os.getcwd(), 'companyprofile_backfill_fixed_errors.log')

        with open(err_log_path, 'a', encoding='utf-8') as elog:
            for i, prof in enumerate(qs[start:end], start=start):
                processed += 1
                if log_every and processed % log_every == 0:
                    self.stdout.write(f'... {start + processed}/{end} processed, {changed} would-change')

                try:
                    c = prof.company
                    data = prof.data if isinstance(prof.data, dict) else {}

                    fixed = build_fixed_companyprofile_payload(c, data)

                    if overwrite:
                        new_data = fixed
                    else:
                        new_data = dict(data)

                    if not overwrite:
                        # 1) top-level corp_name/corp_code ensure
                        if fixed.get('corp_name') is not None:
                            new_data['corp_name'] = fixed.get('corp_name')
                        if fixed.get('corp_code') is not None:
                            new_data['corp_code'] = fixed.get('corp_code')

                        # 2) industry_outlook ensure key exists
                        if 'industry_outlook' not in new_data:
                            new_data['industry_outlook'] = fixed.get('industry_outlook')

                        # 3) normalize stock_code whitespace -> None (keep existing if already canonical)
                        stock_code_canon = _canonical_stock_code(new_data.get('stock_code'))
                        if new_data.get('stock_code') != stock_code_canon:
                            new_data['stock_code'] = stock_code_canon

                        # 4) ensure company_overview exists and contains required keys
                        existing_overview = new_data.get('company_overview')
                        existing_overview = existing_overview if isinstance(existing_overview, dict) else {}
                        fixed_overview = fixed.get('company_overview') or {}

                        merged_overview = dict(existing_overview)
                        # write required keys (do not overwrite non-None with None)
                        for k, v in fixed_overview.items():
                            if v is None and merged_overview.get(k) is not None:
                                continue
                            merged_overview[k] = v

                        # never keep duplicated identifiers inside overview
                        for k in ['corp_name', 'corp_code', 'stock_code']:
                            merged_overview.pop(k, None)

                        new_data['company_overview'] = merged_overview

                        # 5) ensure top-level company_size is consistent with canonical inputs (optional)
                        try:
                            expected_size = classify_company_size(stock_code_canon, new_data.get('financials'))
                        except Exception:
                            expected_size = new_data.get('company_size')

                        if expected_size is not None or new_data.get('company_size') is None:
                            new_data['company_size'] = expected_size

                    # Detect changes
                    if new_data != data:
                        changed += 1
                        if confirm:
                            prof.data = new_data
                            prof.save(update_fields=['data'])

                    if sleep:
                        time.sleep(sleep)

                except Exception as e:
                    try:
                        corp_name = getattr(getattr(prof, 'company', None), 'corp_name', '(unknown)')
                    except Exception:
                        corp_name = '(unknown)'
                    elog.write(f'Error for CompanyProfile id={prof.id} corp_name={corp_name}: {e}\n')
                    elog.flush()

        self.stdout.write(f'Done. Processed: {processed}, Changed: {changed}. Errors: {err_log_path}')
