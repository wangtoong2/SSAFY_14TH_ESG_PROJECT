<script setup>
import { computed, ref, onMounted } from 'vue'
import axios from 'axios'
import { useMainStore } from '@/stores/main'
import {
  mdiAccountMultiple,
  mdiCartOutline,
  mdiChartTimelineVariant,
  mdiMonitorCellphone,
  mdiReload,
  // mdiGithub,
  mdiChartPie,
} from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBoxWidget from '@/components/CardBoxWidget.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import CardBoxTransaction from '@/components/CardBoxTransaction.vue'
import CardBoxClient from '@/components/CardBoxClient.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
// import SectionBannerStarOnGitHub from '@/components/SectionBannerStarOnGitHub.vue'
import { useRouter } from 'vue-router'
import ArticleList from '@/components/ArticleList.vue'

const router = useRouter()
const mainStore = useMainStore()

const clientBarItems = computed(() => mainStore.clients.slice(0, 4))
const transactionBarItems = computed(() => mainStore.history)

const API_BASE = 'http://127.0.0.1:8000'

// recommended companies shown on dashboard (default placeholders)
const recommended = ref([
  { id: 0, corp_name: '기업 이름 추가', number: 512, trend: '12%', trendType: 'up', color: 'text-emerald-500' },
  { id: 1, corp_name: '기업 이름추가', number: 7770, trend: '12%', trendType: 'down', color: 'text-blue-500' },
  { id: 2, corp_name: '기업 이름추가', number: 256, trend: 'Overflow', trendType: 'alert', color: 'text-red-500' },
])

function _shuffle(arr) {
  const a = arr.slice()
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

async function loadRecommendedCompanies() {
  try {
    const r = await axios.get(`${API_BASE}/companies/api/list/`)
    const companies = r.data.companies || []
    if (companies.length === 0) return
    const pick = _shuffle(companies).slice(0, 3)
    // enrich each picked company with profile data (corp_code, company_size, region)
    const enriched = []
    for (let i = 0; i < pick.length; i++) {
      const c = pick[i]
      const item = {
        id: c.id,
        corp_name: c.corp_name || c.name || '',
        corp_code: c.corp_code || c.company_code || '',
        company_size: null,
        region: null,
      }
      try {
        const p = await axios.get(`${API_BASE}/companies/api/companyprofile/summary/?company_id=${encodeURIComponent(c.id)}`)
        console.debug('companyprofile response for', c.id, p.data)
        const pdata = p.data || {}
        const profile = pdata.profile ?? pdata
        // extract fields defensively
        item.company_size = pdata.company_size || profile.company_size || profile.company_overview?.company_size || null
        item.region = pdata.region || profile.region || profile.company_overview?.region || null
        if (!item.corp_code) item.corp_code = pdata.corp_code || profile.corp_code || ''
      } catch (e) {
        console.warn('companyprofile fetch failed for', c.id, e)
      }
      enriched.push(item)
    }
    recommended.value = enriched
    console.debug('Recommended companies loaded (enriched):', recommended.value)
  } catch (e) {
    console.warn('Failed to load recommended companies', e)
  }
}

onMounted(() => {
  loadRecommendedCompanies()
})

// placeholders for the four clickable boxes; edit `title`, `subtitle`, `image`, and `description` here
// `url` may be present but is not displayed. Change these values to customize each box's content.
const transactionBoxes = ref([
  {
    url: 'https://www.saramin.co.kr/',
    image: '',
    title: '사람인 채용 공고',
    subtitle: '채용 정보 확인하기',
    description: '사람인에서 최신 채용 공고를 확인하세요.',
  },
  {
    url: 'https://kr.linkedin.com/',
    image: '',
    title: 'LinkedIn 프로필',
    subtitle: '전문가 네트워크',
    description: 'LinkedIn에서 기업과 인재를 만나보세요.',
  },
])

const clientBoxes = ref([
  {
    url: 'https://www.wanted.co.kr/',
    image: '',
    title: '원티드 채용',
    subtitle: '경력/신입 채용',
    description: '원티드에서 채용 공고와 추천을 확인하세요.',
  },
  {
    url: 'https://www.jobkorea.co.kr/',
    image: '',
    title: '잡코리아 채용',
    subtitle: '기업별 공고 모음',
    description: '잡코리아에서 기업 정보를 확인하세요.',
  },
])

const combinedBoxes = computed(() => [...transactionBoxes.value, ...clientBoxes.value])

</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiChartTimelineVariant" title="주간 추천 기업" main>
        <BaseButton
          :icon="mdiGithub"
          label="글쓰기"
          color="contrast"
          rounded-full
          small
          @click="router.push({name : 'Create'})"
        />
      </SectionTitleLineWithButton>
<!-- 상단바  -->


      <div class="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <CardBox v-for="item in recommended" :key="item.id" class="p-4">
          <div class="flex items-start justify-between">
            <div>
              <div class="text-sm text-gray-500">기업코드: <span class="font-medium">{{ item.corp_code }}</span></div>
              <RouterLink :to="{ name: 'CompanyDetail', params: { id: item.id } }" class="text-lg font-semibold text-blue-600 hover:underline">{{ item.corp_name }}</RouterLink>
              <div class="text-sm text-gray-600">지역 : {{ item.region || '' }}</div>
            <!-- </div>
            <div> -->
            <!-- <div class="text-right"> -->
              <div class="text-sm text-gray-500">
                기업규모 : <span>{{ item.company_size || '-' }}</span></div>
              <!-- <div class="text-2xl font-semibold"> -->
              <!-- <div class="text-sm text-gray-600">
                {{ item.company_size || '-' }}
              </div> -->
            </div>
          </div>
        </CardBox>
      </div>
      
  <!-- 기업 추천 버튼    -->
      <SectionTitleLineWithButton :icon="mdiChartTimelineVariant" title="기업 추천 바로가기" main>
      </SectionTitleLineWithButton>
    
      <CardBox class="mb-6">
        <RouterLink :to="{ name: 'RecommendView' }" class="block p-4 rounded hover:bg-gray-50">
          <h2 class="text-lg font-medium">기업 추천으로 이동</h2>
          <p class="text-sm text-gray-600">추천 페이지에서 조건을 설정하고 기업을 추천받으세요.</p>
        </RouterLink>
      </CardBox>

<!-- 구직사이트 -->
      <SectionTitleLineWithButton :icon="mdiChartTimelineVariant" title="구직 사이트 바로가기" main>
      </SectionTitleLineWithButton>
      <div class="mb-6 grid grid-cols-1 sm:grid-cols-2 gap-6">
        <a
          v-for="(b, idx) in combinedBoxes"
          :key="'box-' + idx"
          :href="b.url || '#'"
          target="_blank"
          rel="noopener"
          class="block"
        >
          <CardBox class="p-4 h-full">
            <div class="flex items-start">
              <img v-if="b.image" :src="b.image" alt="thumb" class="w-14 h-14 rounded object-cover" />
              <div class="ml-4">
                <div class="text-lg font-semibold text-gray-900">{{ b.title || '' }}</div>
                <div class="text-sm text-gray-500">{{ b.subtitle || '' }}</div>
                <div class="mt-2 text-sm text-gray-600">{{ b.description || '' }}</div>
              </div>
            </div>
          </CardBox>
        </a>
      </div>
<!-- 게시판 -->
 
      <SectionTitleLineWithButton :icon="mdiAccountMultiple" title="게시글" />
      <ArticleList />
    </SectionMain>
  </LayoutAuthenticated>
</template>
