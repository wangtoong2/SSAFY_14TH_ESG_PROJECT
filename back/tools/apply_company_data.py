#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import requests

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
ENV = os.path.normpath(os.path.join(ROOT, '..', '.env'))
if os.path.exists(ENV):
    with open(ENV, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#') or '=' not in ln:
                continue
            k, v = ln.split('=', 1)
            k = k.strip(); v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v

KEY = os.environ.get('DART_API_KEY')
if not KEY:
    print('DART_API_KEY not found in env or .env')
    sys.exit(1)

DB = os.path.join(ROOT, 'db.sqlite3')
if not os.path.exists(DB):
    print('DB not found at', DB); sys.exit(1)

def fetch_company_by_corp_code(corp_code):
    url = 'https://opendart.fss.or.kr/api/company.json'
    params = {'crtfc_key': KEY, 'corp_code': corp_code}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def fetch_financials_odr(corp, years=2):
    try:
        from OpenDartReader import OpenDartReader
    except Exception:
        return None
    odr = OpenDartReader(KEY)
    import datetime
    current_year = datetime.date.today().year
    yrs = [current_year - i for i in range(1, years+1)]
    out = {'corp_code': None, 'years': {}, 'latest_year': None, 'revenue_growth': None}
    prev = None
    for y in yrs:
        try:
            df = odr.finstate_all(corp, bsns_year=y, reprt_code='11011', fs_div='CFS')
        except Exception:
            continue
        if df is None or df.empty:
            continue
        if out['corp_code'] is None and hasattr(df, 'corp_code'):
            try:
                out['corp_code'] = df.get('corp_code').iloc[0]
            except Exception:
                pass
        def find_amount(keywords):
            if 'account_nm' not in df.columns:
                return None
            for kw in keywords:
                try:
                    row = df[df['account_nm'].str.contains(kw, na=False)]
                except Exception:
                    continue
                if not row.empty:
                    return _parse_amount(row.iloc[0].get('thstrm_amount'))
            return None
        revenue = find_amount(['매출', '매출액'])
        operating = find_amount(['영업이익'])
        net = find_amount(['당기순이익'])
        out['years'][str(y)] = {'revenue': revenue, 'operating_income': operating, 'net_income': net}
        if prev not in (None, 0) and revenue is not None:
            try:
                out['revenue_growth'] = (revenue - prev) / prev
            except Exception:
                out['revenue_growth'] = None
        prev = revenue
    if out['years']:
        out['latest_year'] = max(map(int, out['years'].keys()))
    return out

def _parse_amount(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    s = str(v).replace(',', '').strip()
    if s in ('', '-', 'None'):
        return None
    try:
        return int(float(s))
    except Exception:
        return None

def classify_size(stock_code, financials):
    if not stock_code and not financials:
        return None
    if stock_code and not financials:
        return '중견'
    years = (financials.get('years') or {}) if financials else {}
    if not years:
        return '중견' if stock_code else None
    latest = financials.get('latest_year')
    rev = None
    if latest and str(latest) in years:
        rev = years[str(latest)].get('revenue')
    if rev is None:
        for y in years.values():
            if y.get('revenue'):
                rev = y.get('revenue'); break
    if rev is None:
        return '중견' if stock_code else None
    if rev >= 1_000_000_000_000:
        return '대기업'
    if rev >= 100_000_000_000:
        return '중견'
    return '중소'

def update_profile_for(corp_code=None, corp_name=None):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if corp_code:
        cur.execute('SELECT id, corp_name, corp_code, stock_code FROM companies_company WHERE corp_code = ?', (corp_code,))
    else:
        cur.execute('SELECT id, corp_name, corp_code, stock_code FROM companies_company WHERE corp_name = ?', (corp_name,))
    row = cur.fetchone()
    if not row:
        print('Company not found')
        return
    company_id = row['id']
    stock_code = row['stock_code']
    print('Found company:', dict(row))

    # fetch company raw
    raw = None
    try:
        raw = fetch_company_by_corp_code(row['corp_code'])
    except Exception as e:
        print('company fetch failed:', e)

    industry_code = None
    industry_name = None
    region = None
    if isinstance(raw, dict):
        industry_code = raw.get('induty_code') or raw.get('induty_cd') or raw.get('induty')
        industry_name = raw.get('stock_name') or raw.get('corp_name')
        region = raw.get('adres') or raw.get('addr') or raw.get('address')

    # fetch financials via OpenDartReader if possible
    fin = None
    try:
        fin = fetch_financials_odr(row['corp_code'])
    except Exception as e:
        print('financial fetch error:', e)

    # load existing profile
    cur.execute('SELECT data FROM companies_companyprofile WHERE company_id = ?', (company_id,))
    pr = cur.fetchone()
    if pr and pr[0]:
        try:
            data = json.loads(pr[0])
        except Exception:
            data = pr[0]
            if not isinstance(data, dict):
                data = {}
    else:
        data = {}

    co = data.get('company_overview') or {}
    if industry_code:
        co['industry_code'] = industry_code
    if industry_name:
        co['industry_name'] = industry_name
    if region:
        co['region'] = region
    # only store raw when it's a valid company payload (skip API error payloads)
    if raw and isinstance(raw, dict):
        status = str(raw.get('status',''))
        message = str(raw.get('message',''))
        if not (status.startswith('0') and '사용한도' in message):
            if not co.get('raw'):
                co['raw'] = raw
    data['company_overview'] = co
    if fin:
        data['financials'] = fin

    # recompute company_size
    data['company_size'] = classify_size(stock_code, data.get('financials'))

    # write back
    cur.execute('UPDATE companies_companyprofile SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE company_id = ?', (json.dumps(data, ensure_ascii=False), company_id))
    con.commit()
    print('Updated profile for company_id=', company_id)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    con.close()

if __name__ == '__main__':
    # default to corp_code from prior lookup
    update_profile_for(corp_code='00434003')
