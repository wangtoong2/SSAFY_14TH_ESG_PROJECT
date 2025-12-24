from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
import logging
from rest_framework.response import Response
from rest_framework import status
from .services import (
    recommend_companies,
    fetch_company_data,
    classify_company_size,
    # build_fixed_companyprofile_payload,
    call_gpt_for_recommendations,
    score_company_for_user,
)
from .models import Company, CompanyProfile
from .serializers import PreferencesSerializer
from rest_framework import serializers
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
                data['corp_code'] = c.corp_code
                canonical_stock_code = (c.stock_code or '').strip() or None
                data['stock_code'] = canonical_stock_code

                # Avoid duplicated identifiers inside company_overview
                try:
                    overview = data.get('company_overview') if isinstance(data, dict) else None
                    if isinstance(overview, dict):
                        for k in ['corp_name', 'corp_code', 'stock_code']:
                            overview.pop(k, None)
                        data['company_overview'] = overview
                except Exception:
                    pass
                try:
                    data['company_size'] = classify_company_size(canonical_stock_code, data.get('financials'))
                except Exception:
                    pass

                try:
                    if isinstance(data.get('company_overview'), dict):
                        data['company_overview']['company_size'] = data.get('company_size')
                except Exception:
                    pass
                CompanyProfile.objects.update_or_create(company=c, defaults={'data': data})
            except Exception as e:
                return Response({'error': f'Failed to fetch profile: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(build_fixed_companyprofile_payload(c, data))


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


class GPTRecommendCompanies(APIView):
    """POST { region, industry, size, top_n, use_gpt } -> GPT-ranked recommendations

    - `region`: string (e.g., '서울특별시')
    - `industry`: string or list
    - `size`: string or list (e.g., '중소','중견','대기업')
    - `top_n`: int
    - `use_gpt`: bool (default True)
    """

    def post(self, request):
        try:
            body = request.data or {}
        except ParseError as pe:
            logging.getLogger(__name__).exception('Failed parsing request body')
            return Response({'error': 'Invalid JSON body', 'details': str(pe)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.getLogger(__name__).exception('Unexpected error reading request body')
            return Response({'error': 'Failed to read request body', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        region = body.get('region')
        industry = body.get('industry')
        size = body.get('size')
        try:
            top_n = int(body.get('top_n') or 10)
        except Exception:
            top_n = 10
        use_gpt = bool(body.get('use_gpt', True))

        # Normalize prefs to match services.recommend_companies
        prefs = {}
        if industry:
            if isinstance(industry, (list, tuple)):
                prefs['desired_industries'] = industry
            else:
                prefs['desired_industries'] = [s.strip() for s in str(industry).split(',') if s.strip()]
        if size:
            if isinstance(size, (list, tuple)):
                prefs['desired_size'] = size
            else:
                prefs['desired_size'] = [s.strip() for s in str(size).split(',') if s.strip()]
        if region:
            prefs['location'] = region

        try:
            candidates = recommend_companies(prefs, top_n=50)
        except Exception as e:
            return Response({'error': f'Recommendation error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If client provided an explicit list of company ids, limit candidates to those
        selected_ids = body.get('selected_company_ids')
        if selected_ids:
            try:
                # normalize ids to ints
                selected_ids = [int(x) for x in selected_ids]
                qs = Company.objects.filter(id__in=selected_ids).select_related('profile')
                candidates = []
                for c in qs:
                    prof = getattr(c, 'profile', None)
                    data = prof.data if prof and prof.data else {}
                    # ensure company_size
                    if data.get('company_size') is None:
                        try:
                            data['company_size'] = classify_company_size(c.stock_code, data.get('financials'))
                        except Exception:
                            data['company_size'] = None

                    score, breakdown = score_company_for_user(prefs, data)
                    candidates.append({
                        'company_id': c.id,
                        'corp_name': c.corp_name,
                        'company_size': data.get('company_size'),
                        'score': score,
                        'breakdown': breakdown,
                        'profile': data,
                    })
                # keep top ordering
                candidates.sort(key=lambda x: x['score'], reverse=True)
            except Exception as e:
                return Response({'error': f'Invalid selected_company_ids: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        if use_gpt:
            ranked = call_gpt_for_recommendations(prefs, candidates, top_n=top_n)
            return Response({'results': ranked})

        # fallback: return top N candidates from deterministic recommender
        return Response({'results': candidates[:top_n]})


class CompanyList(APIView):
    """Return a lightweight list of companies for front-end selection."""

    class OutSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        corp_name = serializers.CharField()
        corp_code = serializers.CharField(allow_null=True)

    def get(self, request):
        qs = Company.objects.all().order_by('corp_name')[:500]
        out = [{'id': c.id, 'corp_name': c.corp_name, 'corp_code': c.corp_code} for c in qs]
        return Response({'companies': out})
