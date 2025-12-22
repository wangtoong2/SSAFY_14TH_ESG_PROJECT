from django.core.management.base import BaseCommand
from companies.models import CompanyProfile
from companies.services import _extract_industry_fields_from_raw


class Command(BaseCommand):
    help = 'Backfill industry_code and industry_name into CompanyProfile.data from stored raw overview'

    def handle(self, *args, **options):
        qs = CompanyProfile.objects.all()
        total = qs.count()
        self.stdout.write(f"Starting backfill for {total} profiles")
        for i, p in enumerate(qs, 1):
            data = p.data or {}
            overview = data.get('company_overview') or {}
            raw = overview.get('raw') if isinstance(overview, dict) else None
            if not raw:
                continue
            norm = _extract_industry_fields_from_raw(raw)
            changed = False
            if norm.get('industry_code') and overview.get('industry_code') != norm['industry_code']:
                overview['industry_code'] = norm['industry_code']
                changed = True
            if norm.get('industry_name') and overview.get('industry_name') != norm['industry_name']:
                overview['industry_name'] = norm['industry_name']
                changed = True
            if changed:
                data['company_overview'] = overview
                p.data = data
                p.save(update_fields=['data', 'updated_at'])
                self.stdout.write(f"[{i}/{total}] Updated {p.company.corp_name}")
            if i % 100 == 0:
                self.stdout.write(f"Processed {i}/{total}")

        self.stdout.write("Backfill complete")
