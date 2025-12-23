#!/usr/bin/env python3
import os
import sqlite3
import json

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db.sqlite3')
DB = os.path.normpath(DB)
print('DB path:', DB)
if not os.path.exists(DB):
    print('DB file not found')
    exit(1)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute('SELECT id, corp_name, corp_code, stock_code FROM companies_company LIMIT 1')
row = cur.fetchone()
if not row:
    print('No company rows')
    exit(0)

company_id = row['id']
print('Company:', dict(row))

cur.execute('SELECT data FROM companies_companyprofile WHERE company_id = ?', (company_id,))
pr = cur.fetchone()
if not pr:
    print('No CompanyProfile for this company')
    exit(0)

try:
    data = json.loads(pr['data']) if isinstance(pr['data'], str) else pr['data']
except Exception:
    # sqlite3 may return JSON as text — attempt raw print
    try:
        data = json.loads(pr[0])
    except Exception:
        data = pr[0]

print('\nProfile keys:', list(data.keys()) if isinstance(data, dict) else type(data))
if isinstance(data, dict):
    co = data.get('company_overview') or {}
    print('\ncompany_overview keys:', list(co.keys()))
    print('industry:', co.get('industry'))
    print('industry_code:', co.get('industry_code'))
    print('industry_name:', co.get('industry_name'))
    print('\ncompany_size:', data.get('company_size'))
    print('\nfinancials available:', 'years' in (data.get('financials') or {}))

con.close()
