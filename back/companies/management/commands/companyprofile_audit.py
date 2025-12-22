import json
from collections import Counter

from django.core.management.base import BaseCommand

from companies.models import CompanyProfile
from companies.services import classify_company_size


REQUIRED_OVERVIEW_KEYS = ['ceo_nm', 'addr', 'industry', 'industry_code', 'region', 'raw']
DUPLICATED_OVERVIEW_KEYS = ['corp_name', 'corp_code', 'stock_code']


def _canonical_stock_code(v):
    if v is None:
        return None
    s = str(v)
    s2 = s.strip()
    return s2 or None


class Command(BaseCommand):
    help = (
        "Audit CompanyProfile.data consistency. "
        "Reports counts for null/blank fields and optionally deep-scans profiles to find mismatches."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--deep',
            action='store_true',
            help='Deep-scan all CompanyProfile rows in Python (slower, but detects whitespace and schema issues).',
        )
        parser.add_argument(
            '--samples',
            type=int,
            default=5,
            help='How many example corp_names to print per issue type (deep scan only).',
        )
        parser.add_argument(
            '--max-scan',
            type=int,
            default=0,
            help='Max profiles to scan in deep mode (0 = all).',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            dest='as_json',
            help='Output summary as JSON.',
        )

    def handle(self, *args, **options):
        deep = bool(options.get('deep'))
        samples = int(options.get('samples') or 0)
        max_scan = int(options.get('max_scan') or 0)
        as_json = bool(options.get('as_json'))

        qs = CompanyProfile.objects.select_related('company')
        total = qs.count()

        # Fast DB-level counts (cheap)
        fast = {
            'profiles_total': total,
            'data_missing': qs.filter(data__isnull=True).count(),
            'company_overview_missing': qs.filter(data__company_overview__isnull=True).count(),
            'financials_null': qs.filter(data__financials__isnull=True).count(),
            'company_size_null': qs.filter(data__company_size__isnull=True).count(),
            'corp_code_null': qs.filter(data__corp_code__isnull=True).count(),
            'stock_code_null': qs.filter(data__stock_code__isnull=True).count(),
            'industry_code_null': qs.filter(data__company_overview__industry_code__isnull=True).count(),
            'region_null': qs.filter(data__company_overview__region__isnull=True).count(),
        }

        if not deep:
            if as_json:
                self.stdout.write(json.dumps({'mode': 'fast', 'counts': fast}, ensure_ascii=False, indent=2))
            else:
                self.stdout.write('[FAST] CompanyProfile audit counts')
                for k, v in fast.items():
                    self.stdout.write(f'- {k}: {v}')
                self.stdout.write('\nTip: run with --deep to detect whitespace stock_code, schema-missing keys, and size mismatches.')
            return

        # Deep scan (Python) for whitespace/consistency/mismatch issues
        counters = Counter()
        example = {
            'stock_code_whitespace': [],
            'stock_code_blank': [],
            'size_mismatch': [],
            'overview_missing_keys': [],
            'overview_has_duplicated_ids': [],
        }

        # Stream rows to keep memory low
        scanned = 0
        iterator = qs.only('id', 'data', 'company__corp_name').iterator(chunk_size=500)
        for prof in iterator:
            scanned += 1
            if max_scan and scanned > max_scan:
                break

            data = prof.data if isinstance(prof.data, dict) else {}
            corp_name = getattr(getattr(prof, 'company', None), 'corp_name', None) or '(unknown)'

            stock_code_raw = data.get('stock_code')
            stock_code_str = None if stock_code_raw is None else str(stock_code_raw)
            stock_code_canon = _canonical_stock_code(stock_code_raw)

            if stock_code_raw is None:
                counters['stock_code_none'] += 1
            else:
                if stock_code_str == '':
                    counters['stock_code_blank'] += 1
                    if samples and len(example['stock_code_blank']) < samples:
                        example['stock_code_blank'].append(corp_name)
                elif stock_code_canon is None:
                    # non-empty string but becomes empty after strip => whitespace
                    counters['stock_code_whitespace'] += 1
                    if samples and len(example['stock_code_whitespace']) < samples:
                        example['stock_code_whitespace'].append(corp_name)
                else:
                    counters['stock_code_present'] += 1

            financials = data.get('financials')
            size_saved = data.get('company_size')
            try:
                size_expected = classify_company_size(stock_code_canon, financials)
            except Exception:
                size_expected = size_saved

            if size_saved != size_expected:
                counters['size_mismatch'] += 1
                if samples and len(example['size_mismatch']) < samples:
                    example['size_mismatch'].append(
                        {
                            'corp_name': corp_name,
                            'saved': size_saved,
                            'expected': size_expected,
                            'stock_code_raw': stock_code_raw,
                        }
                    )

            overview = data.get('company_overview')
            if isinstance(overview, dict):
                missing = [k for k in REQUIRED_OVERVIEW_KEYS if k not in overview]
                if missing:
                    counters['overview_missing_keys'] += 1
                    if samples and len(example['overview_missing_keys']) < samples:
                        example['overview_missing_keys'].append({'corp_name': corp_name, 'missing': missing})

                duplicated = [k for k in DUPLICATED_OVERVIEW_KEYS if k in overview]
                if duplicated:
                    counters['overview_has_duplicated_ids'] += 1
                    if samples and len(example['overview_has_duplicated_ids']) < samples:
                        example['overview_has_duplicated_ids'].append({'corp_name': corp_name, 'keys': duplicated})

        result = {
            'mode': 'deep',
            'fast_counts': fast,
            'deep_counts': dict(counters),
            'scanned': scanned if not max_scan else min(scanned, max_scan),
            'examples': example,
        }

        if as_json:
            self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            self.stdout.write('[DEEP] CompanyProfile audit')
            self.stdout.write(f'- scanned: {result["scanned"]} / profiles_total: {total}')
            self.stdout.write('\n[Fast counts]')
            for k, v in fast.items():
                self.stdout.write(f'- {k}: {v}')

            self.stdout.write('\n[Deep counts]')
            for k, v in sorted(counters.items()):
                self.stdout.write(f'- {k}: {v}')

            if samples:
                self.stdout.write('\n[Examples]')
                for k, v in example.items():
                    if v:
                        self.stdout.write(f'- {k}: {v}')
