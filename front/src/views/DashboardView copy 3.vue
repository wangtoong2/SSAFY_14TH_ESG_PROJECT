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
      <!-- Centered big logo area like Google -->
      <div class="flex flex-col items-center justify-center py-16">
        <RouterLink :to="{ name: 'dashboard' }" class="inline-block">
          <img src="../../public/jobffy_logo.png" alt="logo" class="w-72 h-auto drop-shadow-xl" />
        </RouterLink>
        <p class="mt-4 text-sm text-slate-500 dark:text-slate-300">ESG 기반 추천으로 원하는 기업을 빠르게 찾아보세요.</p>
      </div>

      <!-- Menu bar (AI 추천 | 게시판 | 구직 사이트 바로가기) -->
      <div class="mb-8 flex justify-center w-full px-6 lg:px-12">
        <div class="flex flex-wrap items-center justify-center gap-3 text-sm text-slate-700 dark:text-slate-200 select-none">
          <RouterLink
            :to="{ name: 'RecommendView' }"
            class="px-2 py-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
          >
            기업 AI 추천 받기
          </RouterLink>
          <span class="text-slate-300 dark:text-slate-600">|</span>
          <RouterLink
            :to="{ name: 'ArticleList' }"
            class="px-2 py-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
          >
            게시판
          </RouterLink>
          <span class="text-slate-300 dark:text-slate-600">|</span>

          <div class="relative group">
            <button
              type="button"
              class="px-2 py-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
            >
              구직 사이트 바로가기
            </button>
            <div
              class="hidden group-hover:block group-focus-within:block absolute left-1/2 -translate-x-1/2 mt-2 w-64 bg-white dark:bg-slate-800 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.12)] overflow-hidden z-10 ring-1 ring-black/5 dark:ring-white/10"
            >
              <a
                v-for="link in combinedBoxes"
                :key="link.url"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="block px-4 py-3 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                {{ link.title }}
              </a>
            </div>
          </div>
        </div>
      </div>

      <SectionTitleLineWithButton :icon="mdiChartTimelineVariant" title="주간 추천 기업" main />
<!-- 상단바  -->


      <div class="mb-8 grid grid-cols-1 gap-6 w-full px-6 lg:px-12">
        <div v-for="item in recommended" :key="item.id" class="relative">
          <div class="bg-surface rounded-2xl p-6 shadow-[0_6px_18px_rgba(0,0,0,0.08)] hover:shadow-[0_10px_30px_rgba(0,0,0,0.12)] transition-shadow duration-200">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center text-white font-semibold text-lg">{{ item.corp_name ? item.corp_name.charAt(0) : '?' }}</div>
              <div class="flex-1">
                <RouterLink :to="{ name: 'CompanyDetail', params: { id: item.id } }" class="text-xl font-semibold text-slate-900 hover:underline">{{ item.corp_name }}</RouterLink>
                <div class="mt-1 text-sm text-slate-500">{{ item.corp_code ? `기업코드: ${item.corp_code}` : '' }}</div>
                <div class="mt-2 text-sm text-slate-600">지역: {{ item.region || '-' }} · 규모: {{ item.company_size || '-' }}</div>
              </div>
              <div class="ml-3">
                <RouterLink :to="{ name: 'CompanyDetail', params: { id: item.id } }" class="inline-block px-3 py-1 rounded-full bg-primary text-white text-sm">자세히</RouterLink>
              </div>
            </div>
          </div>
        </div>
      </div>
      

    </SectionMain>
  </LayoutAuthenticated>
</template>
