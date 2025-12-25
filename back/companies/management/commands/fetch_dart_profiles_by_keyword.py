import os
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from companies.models import Company, CompanyProfile
from companies.services import build_fixed_companyprofile_payload, classify_company_size, fetch_company_data


class Command(BaseCommand):
    help = (
        "Fetch and cache DART-based profile data (CompanyProfile) for companies whose name matches a keyword.\n"
        "Typical usage: keyword='삼성' to fetch Samsung-related companies.\n"
        "Requires companies to exist in DB first (run fetch_dart_companies)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--keyword',
            dest='keyword',
            default='삼성',
            help='Substring to match in Company.corp_name (default: 삼성)',
        )
        parser.add_argument(
            '--limit',
            dest='limit',
            type=int,
            default=50,
            help='Max number of companies to process (default: 50)',
        )
        parser.add_argument(
            '--sleep',
            dest='sleep',
            type=float,
            default=0.1,
            help='Seconds to sleep between requests (default: 0.1)',
        )
        parser.add_argument(
            '--log-every',
            dest='log_every',
            type=int,
            default=10,
            help='Print progress every N companies (default: 10). Use 1 for verbose.',
        )
        parser.add_argument(
            '--refresh',
            dest='refresh',
            action='store_true',
            help='Re-fetch even if CompanyProfile already exists',
        )
        parser.add_argument(
            '--print-only',
            dest='print_only',
            action='store_true',
            help='Only print matched companies (no API calls, no DB writes)',
        )

    def handle(self, *args, **options):
        keyword = (options.get('keyword') or '').strip()
        limit = int(options.get('limit') or 50)
        sleep_s = float(options.get('sleep') or 0.0)
        log_every = int(options.get('log_every') or 0)
        refresh = bool(options.get('refresh'))
        print_only = bool(options.get('print_only'))

        if not keyword:
            self.stderr.write('keyword is empty. Provide --keyword.')
            return

        # Ensure API key exists for DART/OpenDartReader usage.
        api_key = os.environ.get('DART_API_KEY') or getattr(settings, 'DART_API_KEY', None)
        if not api_key:
            self.stderr.write(
                'DART API key not provided. Set settings.DART_API_KEY or env DART_API_KEY before fetching profiles.'
            )
            self.stderr.write('Tip: you can still run with --print-only without an API key.')
            if not print_only:
                return

        qs = Company.objects.filter(corp_name__icontains=keyword).order_by('corp_name')
        total = qs.count()
        if total == 0:
            self.stderr.write(
                f"No companies matched keyword '{keyword}'. If DB is empty, run: python manage.py fetch_dart_companies"
            )
            return

        total_to_process = min(total, limit) if limit and limit > 0 else total
        self.stdout.write(
            f"Matched {total} companies for keyword='{keyword}'. Processing {total_to_process}..."
        )

        processed = 0
        skipped = 0
        updated = 0
        created = 0
        errors = 0

        started_at = time.time()

        def _progress_line(i, c_name):
            elapsed = max(0.001, time.time() - started_at)
            rate = i / elapsed
            remaining = max(0, total_to_process - i)
            eta_s = int(remaining / rate) if rate > 0 else 0
            return (
                f"[{i}/{total_to_process}] {c_name} | "
                f"created={created}, updated={updated}, skipped={skipped}, errors={errors} "
                f"(eta~{eta_s}s)"
            )

        for i, c in enumerate(qs[:total_to_process], start=1):
            processed += 1

            if print_only:
                self.stdout.write(
                    f"- {c.id}: {c.corp_name} (corp_code={c.corp_code}, stock_code={c.stock_code or '-'})"
                )
                continue

            if log_every and (i == 1 or i % log_every == 0):
                self.stdout.write(_progress_line(i, c.corp_name))

            existing = CompanyProfile.objects.filter(company=c).first()
            if existing and not refresh:
                skipped += 1
                continue

            try:
                # Prefer corp_code for uniqueness; services handle corp_code for disclosures.
                data = fetch_company_data(c.corp_code or c.corp_name)
                # Normalize core identifiers
                data['corp_name'] = c.corp_name
                data['corp_code'] = c.corp_code
                data['stock_code'] = c.stock_code

                # Ensure company_size is present when possible
                try:
                    if data.get('company_size') is None:
                        data['company_size'] = classify_company_size(c.stock_code, data.get('financials'))
                except Exception:
                    pass

                # Merge into existing schema-stable payload
                existing = existing.data if existing and isinstance(existing.data, dict) else {}
                fixed = build_fixed_companyprofile_payload(c, {**existing, **data})

                # Merge policy: keep existing keys unless new/fixed provides a non-None value.
                merged = dict(existing)
                merged.update({k: v for k, v in fixed.items() if v is not None})

                # Deep-merge company_overview
                existing_ov = merged.get('company_overview') if isinstance(merged.get('company_overview'), dict) else {}
                fixed_ov = fixed.get('company_overview') if isinstance(fixed.get('company_overview'), dict) else {}
                merged_ov = dict(existing_ov)
                merged_ov.update({k: v for k, v in fixed_ov.items() if v is not None or k not in merged_ov})
                for k in ['corp_name', 'corp_code', 'stock_code']:
                    merged_ov.pop(k, None)
                merged['company_overview'] = merged_ov

                obj, was_created = CompanyProfile.objects.update_or_create(company=c, defaults={'data': merged})
                if was_created:
                    created += 1
                else:
                    updated += 1

            except Exception as e:
                errors += 1
                self.stderr.write(f"[ERROR] {c.corp_name} ({c.corp_code}): {e}")

            if log_every and (i == total_to_process):
                self.stdout.write(_progress_line(i, c.corp_name))

            if sleep_s:
                time.sleep(sleep_s)

        if print_only:
            self.stdout.write(self.style.SUCCESS('Done (print-only).'))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. processed={processed}, created={created}, updated={updated}, skipped={skipped}, errors={errors}"
            )
        )
