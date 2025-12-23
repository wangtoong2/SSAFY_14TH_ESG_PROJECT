#!/usr/bin/env python3
import os
import json
import sqlite3

DB = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
DB = os.path.normpath(DB)
if not os.path.exists(DB):
    print('DB not found:', DB)
    raise SystemExit(1)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute('SELECT company_id, data FROM companies_companyprofile')
rows = cur.fetchall()
modified = 0
for r in rows:
    cid = r['company_id']
    raw = r['data']
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        continue
    if not isinstance(data, dict):
        continue
    co = data.get('company_overview') or {}
    rr = co.get('raw')
    if isinstance(rr, dict):
        status = str(rr.get('status',''))
        msg = str(rr.get('message',''))
        if status.startswith('0') and '사용한도' in msg:
            co.pop('raw', None)
            data['company_overview'] = co
            cur.execute('UPDATE companies_companyprofile SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE company_id = ?', (json.dumps(data, ensure_ascii=False), cid))
            modified += 1

con.commit()
con.close()
print('Cleaned', modified, 'profiles with API limit raw errors')
