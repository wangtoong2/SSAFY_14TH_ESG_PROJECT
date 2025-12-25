<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton title="기업 추천" :icon="mdiChartPie" />

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <!-- Left: filters -->
        <div>
          <CardBox is-form @submit.prevent="submit">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <FormField label="지역">
                  <select v-model="form.region" class="mt-1 block w-full border rounded p-2 bg-white text-slate-900 dark:bg-slate-800 dark:text-slate-100 dark:border-slate-600">
                    <option value="">전체</option>
                    <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
                  </select>
                </FormField>
              </div>

              <div>
                <FormField label="산업분야">
                  <select v-model="form.industry" class="mt-1 block w-full border rounded p-2 bg-white text-slate-900 dark:bg-slate-800 dark:text-slate-100 dark:border-slate-600">
                    <option value="">전체</option>
                    <option v-for="ind in industries" :key="ind" :value="ind">{{ ind }}</option>
                  </select>
                </FormField>
              </div>

              <div>
                <FormField label="기업 규모">
                  <select v-model="form.size" class="mt-1 block w-full border rounded p-2 bg-white text-slate-900 dark:bg-slate-800 dark:text-slate-100 dark:border-slate-600">
                    <option value="">전체</option>
                    <option value="중소">중소</option>
                    <option value="중견">중견</option>
                    <option value="대기업">대기업</option>
                  </select>
                </FormField>
              </div>

              <div>
                <FormField label="결과 개수">
                  <input type="number" v-model.number="form.top_n" min="1" max="50" class="mt-1 block w-full border rounded p-2 bg-white text-slate-900 dark:bg-slate-800 dark:text-slate-100 dark:border-slate-600" />
                </FormField>
              </div>
            </div>

            <div class="flex items-center gap-4">
              <BaseButton :disabled="loading" color="info" type="submit" :label="loading ? '조회중...' : '추천 받기'" />
            </div>
          </CardBox>
        </div>

        <!-- Right: results -->
        <div>
          <CardBox>
            <div v-if="error" class="text-red-600 mb-4">{{ error }}</div>

            <div v-if="results && results.length">
              <ul class="space-y-3">
                <li v-for="item in results" :key="item.company_id || item.id" class="p-3 border rounded dark:border-slate-700 dark:bg-slate-900/40">
                  <div class="flex justify-between items-start">
                    <div>
                      <RouterLink :to="{ name: 'CompanyDetail', params: { id: item.company_id || item.id } }" class="font-semibold text-blue-600 hover:underline dark:text-blue-400">
                        {{ getCompanyName(item) || '회사명' }}
                      </RouterLink>
                    </div>
                    <div class="text-right">
                      <div v-if="item.rank" class="text-sm font-medium">Rank: {{ item.rank }}</div>
                      <div v-else-if="item.score" class="text-sm font-medium">Score: {{ item.score ? Number(item.score).toFixed(2) : '-' }}</div>
                    </div>
                  </div>
                  <div class="mt-2 text-sm text-gray-800 dark:text-slate-200">{{ item.reason || (item.breakdown && JSON.stringify(item.breakdown)) || (item.profile && item.profile.recommend_reason) || '' }}</div>
                </li>
              </ul>
            </div>

            <div v-else-if="!loading" class="text-gray-600 dark:text-slate-300">추천 결과가 없습니다. 조건을 입력하고 조회하세요.</div>
          </CardBox>
        </div>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script>
import axios from 'axios'
import { mdiChartPie } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import FormField from '@/components/FormField.vue'
import { RouterLink } from 'vue-router'

export default {
  name: 'RecommendView',
  components: { SectionMain, CardBox, BaseButton, SectionTitleLineWithButton, LayoutAuthenticated, FormField, RouterLink },
  data() {
    return {
      mdiChartPie,
      regions: ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시', '제주특별자치도', '경기도'],
      // KSIC major sections (based on 2-digit ranges)
      industries: [
        '농업, 임업 및 어업',
        '광업',
        '제조업',
        '전기, 가스, 증기 및 공기조절 공급업',
        '건설업',
        '도매 및 소매업',
        '운수 및 창고업',
        '숙박 및 음식점업',
        '정보통신업',
        '금융 및 보험업',
        '부동산업',
        '전문, 과학 및 기술 서비스업',
      ],
      form: {
        region: '서울특별시',
        industry: '',
        size: '',
        top_n: 5,
      },
      loading: false,
      results: null,
      companies: [],
      error: null,
    }
  },

  computed: {
    companyMap() {
      const map = {}
      this.companies.forEach((c) => {
        map[c.id] = c.name || c.corp_name
      })
      return map
    },
  },

  async created() {
    try {
      const API_BASE = 'http://127.0.0.1:8000'
      const r = await axios.get(`${API_BASE}/companies/api/list/`)
      this.companies = r.data.companies || []
    } catch (e) {
      console.warn('Failed to load companies list', e)
    }
  },
  methods: {
  getCompanyName(item) {
    if (!item) return ''

    const companyId = item.company_id || item.id
    if (!companyId) return ''

    // const company = this.companies.find(
    //   (c) => Number(c.id) === Number(companyId)
    // )
    const company = item.corp_name

    // return company?.name || company?.corp_name || '회사명 없음'
    return company || '회사명 없음'
  },
    async submit() {
      this.error = null
      this.results = null
      this.loading = true
      try {
        const payload = {
          region: this.form.region || undefined,
          industry: this.form.industry || undefined,
          size: this.form.size || undefined,
          top_n: this.form.top_n || 10,
          use_gpt: true,
        }

        const API_BASE = 'http://127.0.0.1:8000'
        const resp = await axios.post(`${API_BASE}/companies/api/gpt_recommend/`, payload)
        this.results = resp.data.results || []
        if (resp.data.warning) {
          this.error = resp.data.warning
        }
      } catch (err) {
        console.error(err)
        this.error = err?.response?.data?.error || err.message || '요청 실패'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.input { width: 100%; padding: 0.5rem; border: 1px solid #e5e7eb; border-radius: 0.375rem }

.text-muted { color: #6b7280 }

/* keep profile-like spacing */
.card-actions { margin-top: 1rem }
</style>
