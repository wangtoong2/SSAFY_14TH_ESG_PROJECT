from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
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


def _is_sqlite_locked_error(e: Exception) -> bool:
    msg = str(e).lower()
    return 'database is locked' in msg or 'database table is locked' in msg


def _update_or_create_with_retries(*, company, data, max_retries=8, base_sleep=0.15):
    """Best-effort retries for SQLite concurrent writer locks."""
    last_exc = None
    for attempt in range(max_retries):
        try:
            return CompanyProfile.objects.update_or_create(company=company, defaults={'data': data})
        except OperationalError as e:
            last_exc = e
            if not _is_sqlite_locked_error(e):
                raise
            # backoff with a small cap
            time.sleep(min(base_sleep * (2 ** attempt), 2.0))
    raise last_exc


class Command(BaseCommand):
    help = 'Bulk fetch DART data for all companies and save into CompanyProfile (dry-run unless --confirm)'

    def add_arguments(self, parser):
        parser.add_argument('--sleep', type=float, default=0.05, help='Seconds to sleep between requests')
        parser.add_argument('--start', type=int, default=0, help='Start index (0-based)')
        parser.add_argument('--limit', type=int, default=0, help='Max companies to process (0 = all)')
        parser.add_argument('--confirm', action='store_true', help='Actually perform DB writes')
        parser.add_argument(
            '--key-env',
            type=str,
            default='DART_API_KEY',
            help=(
                'Which environment variable to use for DART key. '
                "Example: --key-env DART_API_KEY2. The selected value will be mapped into DART_API_KEY for this process."
            ),
        )

    def handle(self, *args, **options):
        sleep = options.get('sleep')
        start = options.get('start')
        limit = options.get('limit')
        confirm = options.get('confirm')
        key_env = (options.get('key_env') or 'DART_API_KEY').strip()

        # Allow running multiple processes with different keys by selecting a different env var.
        # We normalize the selected key into DART_API_KEY so downstream code doesn't need to know about key2.
        if key_env != 'DART_API_KEY':
            selected = os.environ.get(key_env)
            if selected:
                os.environ['DART_API_KEY'] = selected
                self.stdout.write(f'Using DART key from env: {key_env} (mapped to DART_API_KEY for this process)')
            else:
                self.stdout.write(f'WARNING: env var {key_env} is not set. Falling back to DART_API_KEY.')

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

                    # Ensure canonical corp_name stored from DB
                    try:
                        data['corp_name'] = c.corp_name
                    except Exception:
                        pass

                    # Ensure canonical corp_code/stock_code stored from DB
                    try:
                        data['corp_code'] = c.corp_code
                    except Exception:
                        pass
                    canonical_stock_code = (c.stock_code or '').strip() or None
                    try:
                        data['stock_code'] = canonical_stock_code
                    except Exception:
                        pass

                    # if overview is missing/invalid, force corp_code-based overview
                    overview = data.get('company_overview') if isinstance(data, dict) else None
                    raw = overview.get('raw') if isinstance(overview, dict) else None
                    raw_status = raw.get('status') if isinstance(raw, dict) else None
                    raw_message = raw.get('message') if isinstance(raw, dict) else None
                    overview_invalid = (not isinstance(overview, dict)) or (raw_status and raw_status != '000')
                    if isinstance(raw_message, str) and 'corp_code' in raw_message:
                        overview_invalid = True

                    # also refetch if key enrichment fields are missing
                    if isinstance(overview, dict):
                        if not (overview.get('industry_code') or overview.get('addr') or overview.get('region')):
                            overview_invalid = True

                    if (overview_invalid) and c.corp_code:
                        try:
                            ov = fetch_company_overview(c.corp_code)
                            if ov:
                                data['company_overview'] = ov
                        except Exception:
                            pass

                    # if still missing financials, try corp_code explicitly
                    if (not data.get('financials')) and c.corp_code:
                        try:
                            fin = fetch_financial_summary(c.corp_code)
                            if fin:
                                data['financials'] = fin
                        except Exception:
                            pass
                    try:
                        data['company_size'] = classify_company_size(canonical_stock_code, data.get('financials'))
                    except Exception:
                        data['company_size'] = data.get('company_size')

                    # also store company_size inside company_overview for fixed schema
                    try:
                        if isinstance(data.get('company_overview'), dict):
                            data['company_overview']['company_size'] = data.get('company_size')
                    except Exception:
                        pass

                    if confirm:
                        try:
                            # merge with existing profile data to avoid accidental overwrite
                            prof = CompanyProfile.objects.filter(company=c).first()
                            if prof and prof.data and isinstance(prof.data, dict):
                                existing = prof.data.copy()
                            else:
                                existing = {}
                            merged = existing.copy()
                            # 기본 정책: None은 기존 값을 덮어쓰지 않는다.
                            merged.update({k: v for k, v in data.items() if v is not None})

                            # 하지만 '없으면 null로 두고 넘어가'가 필요한 키들은,
                            # 기존에 키가 아예 없을 때는 None이라도 명시적으로 채워서 스키마를 안정화한다.
                            required_nullable_keys = [
                                'corp_name',
                                'corp_code',
                                'stock_code',
                                'financials',
                                'company_size',
                                'industry_outlook',
                                'num_disclosures_365d',
                                'latest_disclosures',
                            ]
                            for k in required_nullable_keys:
                                if k not in merged:
                                    merged[k] = data.get(k)
                            # deep merge company_overview
                            existing_co = (existing.get('company_overview') or {}) if isinstance(existing, dict) else {}
                            new_co = (data.get('company_overview') or {}) if isinstance(data, dict) else {}
                            # Do not persist `industry_name` per request
                            if isinstance(new_co, dict) and 'industry_name' in new_co:
                                new_co.pop('industry_name', None)
                            merged_co = existing_co.copy()
                            merged_co.update({k: v for k, v in new_co.items() if v is not None})
                            # avoid duplicated identifiers inside company_overview
                            for k in ['corp_name', 'corp_code', 'stock_code']:
                                merged_co.pop(k, None)

                            # keep company_overview schema stable across companies
                            for k in ['ceo_nm', 'addr', 'industry', 'industry_code', 'induty_code', 'est_dt', 'adres', 'region', 'company_size', 'raw']:
                                if k not in merged_co:
                                    merged_co[k] = None
                            merged['company_overview'] = merged_co

                            _update_or_create_with_retries(company=c, data=merged)
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