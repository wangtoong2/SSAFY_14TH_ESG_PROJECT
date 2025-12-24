from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch

from .models import Company, CompanyProfile


class GPTRecommendEndpointTest(TestCase):
    def setUp(self):
        # create a few companies with simple profile data
        self.c1 = Company.objects.create(corp_code='00000001', corp_name='Alpha Co', stock_code='1001')
        self.c2 = Company.objects.create(corp_code='00000002', corp_name='Beta Inc', stock_code='1002')
        self.c3 = Company.objects.create(corp_code='00000003', corp_name='Gamma LLC', stock_code='')

        CompanyProfile.objects.create(company=self.c1, data={
            'company_overview': {'industry': 'IT', 'addr': '서울특별시 강남구', 'company_size': '중견'},
            'financials': {'years': {'2023': {'revenue': 200000000000}}, 'latest_year': 2023}
        })
        CompanyProfile.objects.create(company=self.c2, data={
            'company_overview': {'industry': 'IT', 'addr': '서울특별시 서초구', 'company_size': '중소'},
            'financials': {'years': {'2023': {'revenue': 50000000000}}, 'latest_year': 2023}
        })
        CompanyProfile.objects.create(company=self.c3, data={
            'company_overview': {'industry': 'Manufacturing', 'addr': '부산광역시', 'company_size': '중소'},
            'financials': {'years': {'2023': {'revenue': 30000000000}}, 'latest_year': 2023}
        })

        self.client = APIClient()

    @patch('companies.api_views.call_gpt_for_recommendations')
    def test_gpt_recommend_endpoint_with_mock(self, mock_gpt):
        # Prepare mocked GPT response
        mock_gpt.return_value = [
            {'company_id': self.c1.id, 'corp_name': 'Alpha Co', 'rank': 1, 'reason': 'Strong revenue and in-region'},
            {'company_id': self.c2.id, 'corp_name': 'Beta Inc', 'rank': 2, 'reason': 'Good fit'}
        ]

        payload = {
            'region': '서울특별시',
            'industry': 'IT',
            'size': '중견',
            'top_n': 2,
            'use_gpt': True,
        }

        resp = self.client.post('/companies/api/gpt_recommend/', payload, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)
        # Ensure returned items match mocked GPT output
        self.assertEqual(data['results'][0]['company_id'], self.c1.id)
        self.assertEqual(data['results'][0]['corp_name'], 'Alpha Co')
        self.assertEqual(data['results'][0]['reason'], 'Strong revenue and in-region')
