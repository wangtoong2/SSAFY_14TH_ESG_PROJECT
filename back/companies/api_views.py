from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import recommend_companies, fetch_company_data, classify_company_size, extract_region_from_address
from .models import Company, CompanyProfile
from .serializers import PreferencesSerializer
from .api import get_all_corporate_disclosure_data


class RecommendCompanies(APIView):
    """POST prefs JSON -> returns top-N company recommendations.

    Example POST body:
    {
      "prefs": { ... },
      "top_n": 10,
      "use_db_cache": true
    }
    """

    def post(self, request):
        body = request.data or {}
        prefs = body.get('prefs') or {}
        top_n = body.get('top_n') or 10
        use_db_cache = body.get('use_db_cache', True)

        serializer = PreferencesSerializer(data=prefs)
        if not serializer.is_valid():
            return Response({'error': 'Invalid prefs', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # The underlying service does not accept use_db_cache; keep param for compatibility
            results = recommend_companies(serializer.validated_data, top_n=top_n)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'results': results})


class CompanyProfileSummary(APIView):
    """GET company profile summary fields (corp_name, industry_code, financials, region).

    Query params:
      - corp_name: company name (preferred)
      - company_id: numeric id (alternative)
    """

    def get(self, request):
        corp_name = request.query_params.get('corp_name')
        company_id = request.query_params.get('company_id')

        c = None
        if corp_name:
            c = Company.objects.filter(corp_name=corp_name).first()
        elif company_id:
            try:
                c = Company.objects.filter(id=int(company_id)).first()
            except Exception:
                c = None

        if not c:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

        # Load or compute profile
        prof = CompanyProfile.objects.filter(company=c).first()
        data = prof.data if prof and prof.data else None
        if not data:
            try:
                data = fetch_company_data(c.corp_code or c.corp_name)
                # ensure stock_code and size
                data['corp_name'] = c.corp_name
                data['stock_code'] = c.stock_code
                try:
                    data['company_size'] = classify_company_size(c.stock_code, data.get('financials'))
                except Exception:
                    pass
                CompanyProfile.objects.update_or_create(company=c, defaults={'data': data})
            except Exception as e:
                return Response({'error': f'Failed to fetch profile: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        overview = (data or {}).get('company_overview') or {}
        industry_code = overview.get('industry_code')
        # If industry_code missing but raw present, try to backfill using existing helper
        if not industry_code and overview.get('raw'):
            try:
                from .services import _extract_industry_fields_from_raw
                norm = _extract_industry_fields_from_raw(overview.get('raw'))
                industry_code = norm.get('industry_code') or industry_code
            except Exception:
                pass

        addr = overview.get('addr')
        region = overview.get('region') or (extract_region_from_address(addr) if addr else None)

        payload = {
            'corp_name': c.corp_name,
            'industry_code': industry_code,
            'financials': data.get('financials') if data else None,
            'region': region,
        }
        return Response(payload)


class UserCompanyRecommendations(APIView):
    """기존 companies/recommend/ 레거시 엔드포인트를 DRF로 제공.

    - 로그인 사용자의 interests/skills를 prefs로 매핑해서 companies.services.recommend_companies 호출
    - 반환 포맷은 레거시와 유사하게 유지: {"results": [...]} 형태
    """

    def get(self, request):
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        interests_raw = getattr(user, 'interests', '') or ''
        skills_raw = getattr(user, 'skills', '') or ''

        # "AI, Blockchain" / "AI,Blockchain" / "AI" 등 허용
        desired_industries = [s.strip() for s in interests_raw.split(',') if s.strip()]
        keywords = [s.strip() for s in skills_raw.split(',') if s.strip()]

        prefs = {
            'desired_industries': desired_industries,
            'keywords': keywords,
        }

        # optional: top_n query param
        try:
            top_n = int(request.query_params.get('top_n') or 10)
        except Exception:
            top_n = 10

        results = recommend_companies(prefs, top_n=top_n)
        return Response({'results': results})


class ParseCorporateDisclosures(APIView):
    """기존 companies/parse/ 레거시 엔드포인트를 DRF로 제공.

    기존과 동일하게 예시 기간을 사용하여 DART 공시를 수집해 DB에 저장한다.
    """

    def post(self, request):
        start_date = '20220101'
        end_date = '20221215'
        try:
            get_all_corporate_disclosure_data(start_date, end_date)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': 'Data fetching and saving completed.'})
