from companies.constants import KSIC_SECTION_MAP
from companies.models import CompanyProfile
import json, pprint

term = 'IT'
matches = [(k, v) for k, v in KSIC_SECTION_MAP.items() if term.lower() in v.lower() or term == k]
print('KSIC matches:', matches)

qs = CompanyProfile.objects.filter(data__isnull=False)
out = []
terml = term.lower()
for p in qs:
    d = p.data if isinstance(p.data, dict) else (json.loads(p.data) if isinstance(p.data, str) else {})
    co = d.get('company_overview') or {}
    ind = co.get('industry') or co.get('industry_name') or co.get('induty_code') or co.get('industry_code')
    if ind and terml in str(ind).lower():
        out.append({
            'company_id': getattr(p.company, 'id', None),
            'corp_name': getattr(p.company, 'corp_name', None),
            'industry': ind,
            'industry_code': co.get('induty_code') or co.get('industry_code')
        })

print('profiles matched:', len(out))
pprint.pprint(out[:200])
