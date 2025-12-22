from django.urls import reverse
from rest_framework.test import APITestCase
from companies.models import Company, CompanyProfile


class RecommendAPITest(APITestCase):
    def setUp(self):
        # create sample companies and profiles
        c1 = Company.objects.create(corp_code='0001', corp_name='테스트A', stock_code='123456')
        c2 = Company.objects.create(corp_code='0002', corp_name='테스트B')
        CompanyProfile.objects.create(company=c1, data={'corp_name': '테스트A', 'company_size': '대기업', 'financials': {'years': {'2023': {'revenue': 2000000000000}}, 'latest_year': 2023, 'revenue_growth': 0.1}})
        CompanyProfile.objects.create(company=c2, data={'corp_name': '테스트B', 'company_size': '중소', 'financials': {'years': {'2023': {'revenue': 50000000000}}, 'latest_year': 2023, 'revenue_growth': 0.02}})

    def test_recommend_default(self):
        url = reverse('api_recommend_companies')
        body = {'prefs': {'desired_industries': [], 'desired_size': ['대기업']}, 'top_n': 2}
        resp = self.client.post(url, data=body, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('results', data)
        self.assertGreaterEqual(len(data['results']), 1)
