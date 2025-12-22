#!/usr/bin/env python3
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ESG.settings')
import django
django.setup()

from companies.models import Company, CompanyProfile
from companies.services import fetch_company_data, classify_company_size

TARGET = os.environ.get('TARGET_COMPANY') or '다코'

c = Company.objects.filter(corp_name=TARGET).first()
if not c:
    print('Company not found:', TARGET)
    sys.exit(1)

print('Updating company:', c.corp_name, 'id=', c.id)

data = fetch_company_data(c.corp_name)
# ensure stock_code and recompute
data['stock_code'] = c.stock_code
try:
    data['company_size'] = classify_company_size(c.stock_code, data.get('financials'))
except Exception:
    pass

# save
p, created = CompanyProfile.objects.update_or_create(company=c, defaults={'data': data})
print('Updated CompanyProfile (created=%s)' % created)
print('\ncompany_overview:', data.get('company_overview'))
print('\nfinancials:', data.get('financials'))
print('\ncompany_size:', data.get('company_size'))

# if company_overview present and contains normalized fields, show them
if isinstance(data.get('company_overview'), dict):
    print('\nindustry_code:', data['company_overview'].get('industry_code'))
    print('industry_name:', data['company_overview'].get('industry_name'))

print('\nDone')
