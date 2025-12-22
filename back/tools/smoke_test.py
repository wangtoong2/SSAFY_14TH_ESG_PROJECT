#!/usr/bin/env python3
import os
import sys
import django
import json

# ensure parent `back` directory is on sys.path so `ESG` package is importable
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ESG.settings')
django.setup()

from companies.models import Company, CompanyProfile
from companies.services import fetch_company_data, recommend_companies, classify_company_size


def main():
    print("SMOKE TEST START")
    c = Company.objects.first()
    if not c:
        print("No Company found in DB")
        return

    print("Sample company:", c.corp_name, "(stock:", c.stock_code, ")")

    try:
        p = CompanyProfile.objects.get(company=c)
        print("Has profile: ", bool(p.data))
    except CompanyProfile.DoesNotExist:
        p = None
        print("No CompanyProfile for sample")

    print("\n--- Live fetch_company_data ---")
    try:
        data = fetch_company_data(c.corp_name)
        print("Fetched keys:", list(data.keys()))
        print("company_overview keys:", list((data.get('company_overview') or {}).keys()))
        print("Computed size (from fetched):", classify_company_size(c.stock_code, data.get('financials')))
    except Exception as e:
        print("fetch_company_data error:", e)

    print("\n--- recommend_companies (top 5) ---")
    try:
        prefs = {'desired_industries': [], 'desired_size': None}
        res = recommend_companies(prefs, top_n=5)
        print("Top results count:", len(res))
        print(json.dumps(res[:3], ensure_ascii=False, indent=2))
    except Exception as e:
        print("recommend_companies error:", e)


if __name__ == '__main__':
    main()
