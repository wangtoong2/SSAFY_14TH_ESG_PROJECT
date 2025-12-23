Recommendation API and cache

1) Migrations

cd back
python manage.py makemigrations companies
python manage.py migrate

2) Generate full cache (writes JSON + DB profiles)

cd back
python manage.py fetch_dart_data --out companies_dart_cache.json --save-db

3) Recommendation API
POST /companies/api/recommend/
Body JSON:
{
  "prefs": { ... },
  "top_n": 10,
  "use_db_cache": true
}

Response: { "results": [ {"company_id":..., "corp_name":..., "score":..., "breakdown": {...}, "profile": {...} }, ... ] }

Notes:
- If you don't want DB caching, pass `--save-db` flag false and `use_db_cache=false` in API.
- Tests: run `python manage.py test companies` to execute the API tests.
