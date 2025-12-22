from django.core.management.base import BaseCommand

from companies.models import Company, CompanyProfile
from companies.services import (
    classify_company_size,
    build_fixed_companyprofile_payload,
    extract_region_from_address,
    fetch_company_data,
)


class Command(BaseCommand):
    help = (
        "Print a compact CompanyProfile summary as JSON. "
        "Fields: corp_name, industry_code, financials, region. "
        "Can optionally refresh from DART and update DB."
    )

    def add_arguments(self, parser):
        parser.add_argument('--corp-name', dest='corp_name', help='Company name (Company.corp_name)')
        parser.add_argument('--company-id', dest='company_id', type=int, help='Company id (Company.id)')
        parser.add_argument(
            '--refresh',
            action='store_true',
            dest='refresh',
            help='Fetch from DART via services.fetch_company_data and update CompanyProfile before printing',
        )

    def handle(self, *args, **options):
        corp_name = options.get('corp_name')
        company_id = options.get('company_id')
        refresh = bool(options.get('refresh'))

        c = None
        if corp_name:
            c = Company.objects.filter(corp_name=corp_name).first()
        elif company_id is not None:
            c = Company.objects.filter(id=company_id).first()

        if not c:
            self.stderr.write('Company not found. Use --corp-name or --company-id.')
            return

        prof = CompanyProfile.objects.filter(company=c).first()
        data = prof.data if prof and prof.data else None

        if refresh or not data:
            data = fetch_company_data(c.corp_code or c.corp_name)
            data['corp_name'] = c.corp_name
            data['corp_code'] = c.corp_code
            canonical_stock_code = (c.stock_code or '').strip() or None
            data['stock_code'] = canonical_stock_code

            # Avoid duplicated identifiers inside company_overview
            try:
                overview = data.get('company_overview') if isinstance(data, dict) else None
                if isinstance(overview, dict):
                    for k in ['corp_name', 'corp_code', 'stock_code']:
                        overview.pop(k, None)
                    data['company_overview'] = overview
            except Exception:
                pass
            try:
                data['company_size'] = classify_company_size(canonical_stock_code, data.get('financials'))
            except Exception:
                pass

            try:
                if isinstance(data.get('company_overview'), dict):
                    data['company_overview']['company_size'] = data.get('company_size')
            except Exception:
                pass
            CompanyProfile.objects.update_or_create(company=c, defaults={'data': data})

        overview = (data or {}).get('company_overview') or {}
        payload = build_fixed_companyprofile_payload(c, data)

        # JSON output (ensure_ascii=False for Korean)
        try:
            import json

            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        except Exception:
            # fallback
            self.stdout.write(str(payload))
