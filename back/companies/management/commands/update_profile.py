from django.core.management.base import BaseCommand, CommandError
from companies.models import Company, CompanyProfile
from companies.services import fetch_company_data, classify_company_size, fetch_financial_summary


class Command(BaseCommand):
    help = 'Fetch DART data for one company and update CompanyProfile (usage: manage.py update_profile --corp "회사명")'

    def add_arguments(self, parser):
        parser.add_argument('--corp', '-c', required=True, help='corp_name to update')
        parser.add_argument('--use-corp-code', action='store_true', dest='use_corp_code', help='Use Company.corp_code for lookup when calling DART')

    def handle(self, *args, **options):
        corp = options.get('corp')
        try:
            c = Company.objects.get(corp_name=corp)
        except Company.DoesNotExist:
            raise CommandError(f'Company not found: {corp}')

        self.stdout.write(f'Updating company: {c.corp_name} (id={c.id})')
        # prefer corp_code search if requested and available
        if options.get('use_corp_code') and c.corp_code:
            lookup = c.corp_code
        else:
            lookup = c.corp_name

        data = fetch_company_data(lookup)
        data['stock_code'] = c.stock_code

        # if financials missing, try explicit fetch by corp_code
        if not data.get('financials') and c.corp_code:
            try:
                fin = fetch_financial_summary(c.corp_code)
                if fin:
                    data['financials'] = fin
            except Exception as e:
                self.stdout.write('fetch_financial_summary failed: ' + str(e))

        # compute company_size
        try:
            data['company_size'] = classify_company_size(c.stock_code, data.get('financials'))
        except Exception:
            data['company_size'] = data.get('company_size')

        # normalize region/address from raw overview
        ov = data.get('company_overview') or {}
        raw = ov.get('raw') if isinstance(ov, dict) else None
        region = None
        if isinstance(raw, dict):
            for rk in ('adres', 'addr', 'address', 'adres_kor', 'location'):
                if rk in raw and raw.get(rk):
                    region = raw.get(rk)
                    break
        # fallback to existing addr/addr field in overview
        if not region:
            region = ov.get('addr') or ov.get('adres')
        if region:
            ov['region'] = region
            data['company_overview'] = ov

        # merge with existing profile data to avoid overwriting fields unintentionally
        try:
            prof = CompanyProfile.objects.filter(company=c).first()
            if prof and prof.data and isinstance(prof.data, dict):
                existing = prof.data.copy()
            else:
                existing = {}
        except Exception:
            existing = {}

        # shallow merge: keep existing keys unless new data provides them
        merged = existing.copy()
        merged.update({k: v for k, v in data.items() if v is not None})

        # deep-merge company_overview dict so we don't drop industry/region keys
        existing_co = (existing.get('company_overview') or {}) if isinstance(existing, dict) else {}
        new_co = (data.get('company_overview') or {}) if isinstance(data, dict) else {}
        # Do not persist `industry_name` per request
        if isinstance(new_co, dict) and 'industry_name' in new_co:
            new_co.pop('industry_name', None)
        merged_co = existing_co.copy()
        merged_co.update({k: v for k, v in new_co.items() if v is not None})
        merged['company_overview'] = merged_co

        CompanyProfile.objects.update_or_create(company=c, defaults={'data': merged})

        self.stdout.write('overview_keys: ' + str(list((merged.get('company_overview') or {}).keys())))
        self.stdout.write('industry: ' + str((merged.get('company_overview') or {}).get('industry')))
        self.stdout.write('industry_code: ' + str((merged.get('company_overview') or {}).get('industry_code')))
        self.stdout.write('region: ' + str((merged.get('company_overview') or {}).get('region')))
        self.stdout.write('company_size: ' + str(merged.get('company_size')))
