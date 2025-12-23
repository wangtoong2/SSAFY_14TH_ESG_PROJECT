<template>
  <div class="p-6">
    <h2 class="text-2xl font-semibold mb-4">기업 추천</h2>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div>
        <label class="block text-sm font-medium">지역</label>
        <select v-model="form.region" class="mt-1 block w-full border rounded p-2">
          <option value="">전체</option>
          <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium">산업분야</label>
        <select v-model="form.industry" class="mt-1 block w-full border rounded p-2">
          <option value="">전체</option>
          <option v-for="ind in industries" :key="ind" :value="ind">{{ ind }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium">기업 규모</label>
        <select v-model="form.size" class="mt-1 block w-full border rounded p-2">
          <option value="">전체</option>
          <option value="중소">중소</option>
          <option value="중견">중견</option>
          <option value="대기업">대기업</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium">결과 개수</label>
        <input type="number" v-model.number="form.top_n" min="1" max="50" class="mt-1 block w-full border rounded p-2" />
      </div>
    </div>

    <!-- 회사 목록 UI 제거: 단순 필터/선택 기능은 사용하지 않습니다 -->

    <div class="flex items-center gap-4 mb-6">
      <label class="inline-flex items-center">
        <input type="checkbox" v-model="form.use_gpt" class="mr-2" />
        <span>GPT 재랭킹 사용</span>
      </label>

      <button @click="submit" :disabled="loading" class="bg-blue-600 text-white px-4 py-2 rounded">
        {{ loading ? '조회중...' : '추천 받기' }}
      </button>
    </div>

    <div v-if="error" class="text-red-600 mb-4">{{ error }}</div>

    <div v-if="results && results.length">
      <h3 class="text-xl font-medium mb-2">추천 결과</h3>
      <ul class="space-y-3">
        <li v-for="item in results" :key="item.company_id" class="p-3 border rounded">
          <div class="flex justify-between items-start">
            <div>
              <div class="font-semibold">{{ item.corp_name || item.name || item.company_name }}</div>
              <div class="text-sm text-gray-600">ID: {{ item.company_id || item.id || '-' }}</div>
            </div>
            <div class="text-right">
              <div v-if="item.rank" class="text-sm font-medium">Rank: {{ item.rank }}</div>
              <div v-else-if="item.score" class="text-sm font-medium">Score: {{ item.score.toFixed(2) }}</div>
            </div>
          </div>
          <div class="mt-2 text-sm text-gray-800">{{ item.reason || (item.breakdown && JSON.stringify(item.breakdown)) || '' }}</div>
        </li>
      </ul>
    </div>

    <div v-else-if="!loading" class="text-gray-600">추천 결과가 없습니다. 조건을 입력하고 조회하세요.</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RecommendView',
  data() {
    return {
      regions: ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시', '제주특별자치도', '경기도'],
      industries: ['IT', '제조', '금융', '헬스케어', '서비스', '디자인', '교육', '미디어', '건설', '에너지'],
      form: {
        region: '서울특별시',
        industry: '',
        size: '',
        top_n: 5,
        use_gpt: true,
      },
      loading: false,
      results: null,
      companies: [],
      error: null,
    }
  },
  async created() {
    // fetch company list for selection
    try {
      const r = await axios.get('/companies/api/list/')
      this.companies = r.data.companies || []
    } catch (e) {
      console.warn('Failed to load companies list', e)
    }
  },
    methods: {
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
          use_gpt: this.form.use_gpt,
        }

        const resp = await axios.post('/companies/api/gpt_recommend/', payload)
        this.results = resp.data.results || []
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
/* small adjustments */
</style>
