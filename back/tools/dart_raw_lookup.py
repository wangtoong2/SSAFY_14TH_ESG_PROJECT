#!/usr/bin/env python3
import os
import sys
import json
import requests

# try to load .env from repository root if present
def load_dotenv(path):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#') or '=' not in ln:
                continue
            k, v = ln.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
DOTENV = os.path.join(ROOT, '.env')
load_dotenv(DOTENV)

KEY = os.environ.get('DART_API_KEY')
if not KEY:
    print('DART_API_KEY not set in environment or .env')
    sys.exit(1)

corp_code = '00434003'

try:
    from OpenDartReader import OpenDartReader
except Exception:
    OpenDartReader = None

def print_json(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))

if OpenDartReader:
    try:
        odr = OpenDartReader(KEY)
        print('Using OpenDartReader.company(corp_code)')
        raw = odr.company(corp_code)
        print_json(raw)
    except Exception as e:
        print('OpenDartReader failed:', e)
        # try company_by_name fallback
        try:
            print('Trying company_by_name...')
            lst = odr.company_by_name(corp_code)
            print_json(lst)
        except Exception as e2:
            print('company_by_name failed:', e2)
else:
    # fallback to DART public API
    url = 'https://opendart.fss.or.kr/api/company.json'
    params = {'crtfc_key': KEY, 'corp_code': corp_code}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        j = r.json()
        print_json(j)
    except Exception as e:
        print('HTTP request failed:', e)
