#!/usr/bin/env python3
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ESG.settings')
import django
django.setup()

from companies.models import Company, CompanyProfile
from companies.services import fetch_company_data, classify_company_size

def needs_update(profile_data):
    try:
        if not profile_data:
            return True
        co = profile_data.get('company_overview') if isinstance(profile_data, dict) else None
        if not co:
            return True
        # update if no industry_code present
        if not (co.get('induty_code') or co.get('industry_code')):
            return True
        return False
    except Exception:
        return True

def main():
    qs = Company.objects.all()
    total = qs.count()
    print(f'Found {total} companies')
    for i, c in enumerate(qs, 1):
        try:
            prof = getattr(c, 'profile', None)
            data = prof.data if prof and prof.data else None
            if not needs_update(data):
                print(f'[{i}/{total}] Skipping {c.corp_name} (already has industry code)')
                continue

            print(f'[{i}/{total}] Fetching data for {c.corp_name}')
            new = fetch_company_data(c.corp_name)
            # ensure stock_code and compute company_size
            new['stock_code'] = c.stock_code
            try:
                new['company_size'] = classify_company_size(c.stock_code, new.get('financials'))
            except Exception:
                pass

            CompanyProfile.objects.update_or_create(company=c, defaults={'data': new})
            print(f'  Updated profile for {c.corp_name}')
            time.sleep(0.2)
        except Exception as e:
            print(f'  Failed for {c.corp_name}: {e}')

if __name__ == '__main__':
    main()
