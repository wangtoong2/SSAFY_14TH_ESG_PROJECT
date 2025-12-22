from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import recommend_companies
from .serializers import PreferencesSerializer


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
            results = recommend_companies(serializer.validated_data, top_n=top_n, use_db_cache=use_db_cache)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'results': results})
