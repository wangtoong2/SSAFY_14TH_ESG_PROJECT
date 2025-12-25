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

function isKoreanRegion(region) {
  if (!region) return true
  const r = String(region).trim()
  if (!r) return true

  // Allow common Korean administrative regions.
  const koreanRegionPattern =
    /(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주|특별시|광역시|특별자치시|특별자치도)/
  if (koreanRegionPattern.test(r)) return true

  // If it contains Hangul, treat as domestic (best-effort).
  const hasHangul = /[\u3131-\u318e\uac00-\ud7a3]/.test(r)
  if (hasHangul) return true

  return false
}

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
    const r = await axios.get(`${API_BASE}/companies/api/list/`, { params: { limit: 2000 } })
    const companies = r.data.companies || []
    if (companies.length === 0) return
    const shuffled = _shuffle(companies)

    const TARGET_COUNT = 3
    const BATCH_SIZE = 12
    const MAX_ATTEMPTS = Math.min(shuffled.length, 300)

    const strictPicked = []
    const relaxedPicked = []
    const seenIds = new Set()

    const strictOk = (item) => !!item.region && !!item.company_size && isKoreanRegion(item.region)
    const relaxedOk = (item) => isKoreanRegion(item.region)

    const fetchEnriched = async (c) => {
      const item = {
        id: c.id,
        corp_name: c.corp_name || c.name || '',
        corp_code: c.corp_code || c.company_code || '',
        company_size: null,
        region: null,
      }

      try {
        const p = await axios.get(
          `${API_BASE}/companies/api/companyprofile/summary/?company_id=${encodeURIComponent(c.id)}`
        )
        const pdata = p.data || {}
        const profile = pdata.profile ?? pdata

        item.company_size =
          pdata.company_size || profile.company_size || profile.company_overview?.company_size || null
        item.region = pdata.region || profile.region || profile.company_overview?.region || null
        if (!item.corp_code) item.corp_code = pdata.corp_code || profile.corp_code || ''
      } catch (e) {
        // Summary fetch can fail; keep base info and handle with relaxed/fallback selection.
        console.warn('companyprofile fetch failed for', c.id, e)
      }

      return item
    }

    // Prefer strict picks (region + size + domestic). If insufficient, fill with relaxed picks.
    for (let start = 0; start < MAX_ATTEMPTS && strictPicked.length < TARGET_COUNT; start += BATCH_SIZE) {
      const slice = shuffled.slice(start, Math.min(start + BATCH_SIZE, MAX_ATTEMPTS))
      const items = await Promise.all(slice.map(fetchEnriched))

      for (const item of items) {
        if (!item || seenIds.has(item.id)) continue
        seenIds.add(item.id)

        if (strictOk(item)) {
          strictPicked.push(item)
          if (strictPicked.length >= TARGET_COUNT) break
        } else if (relaxedOk(item)) {
          relaxedPicked.push(item)
        }
      }
    }

    const finalPicked = strictPicked.slice(0, TARGET_COUNT)
    if (finalPicked.length < TARGET_COUNT) {
      for (const item of relaxedPicked) {
        if (finalPicked.length >= TARGET_COUNT) break
        if (seenIds.has(item.id) && finalPicked.some((x) => x.id === item.id)) continue
        finalPicked.push(item)
      }
    }

    // Last-resort: if we still can't reach 3 (e.g., very sparse profile data), fill with any companies.
    if (finalPicked.length < TARGET_COUNT) {
      for (let i = 0; i < shuffled.length && finalPicked.length < TARGET_COUNT; i++) {
        const c = shuffled[i]
        if (!c || seenIds.has(c.id)) continue
        seenIds.add(c.id)
        finalPicked.push({
          id: c.id,
          corp_name: c.corp_name || c.name || '',
          corp_code: c.corp_code || c.company_code || '',
          company_size: null,
          region: null,
        })
      }
    }

    if (finalPicked.length > 0) {
      recommended.value = finalPicked.slice(0, TARGET_COUNT)
    }
    // 디버깅용 로그: 추천 기업 로드 결과 확인용(배포/제출 시 비활성화)
    // console.debug('Recommended companies loaded (enriched):', recommended.value)
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
      <div class="flex flex-col items-center justify-center pt-12 pb-8">
        <RouterLink :to="{ name: 'dashboard' }" class="inline-block">
          <img src="../../public/jobffy_logo.png" alt="logo" class="w-80 md:w-96 h-auto drop-shadow-xl" />
        </RouterLink>
        <p class="mt-3 text-sm text-slate-500 dark:text-slate-300">AI 기반 추천으로 원하는 기업을 빠르게 찾아보세요.</p>
      </div>

      <!-- Menu bar (AI 추천 | 게시판 | 구직 사이트 바로가기) -->
      <div class="mb-8 flex justify-center w-full px-6 lg:px-12">
        <div class="flex flex-wrap items-center justify-center gap-3 text-base text-slate-700 dark:text-slate-200 select-none">
          <RouterLink
            :to="{ name: 'RecommendView' }"
            class="px-2 py-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
          >
            기업 AI 추천 받기
          </RouterLink>
          <span class="text-slate-300 dark:text-slate-600">|</span>
          <RouterLink
            :to="{ name: 'CompanySearch' }"
            class="px-2 py-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
          >
            기업 검색하기
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
          <div class="bg-white rounded-2xl p-6 shadow-[0_6px_18px_rgba(0,0,0,0.08)] hover:shadow-[0_10px_30px_rgba(0,0,0,0.12)] transition-shadow duration-200">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-xl bg-white flex items-center justify-center overflow-hidden">
                <img src="/companyicon.png" alt="회사 아이콘" class="w-10 h-10 object-contain" draggable="false" />
              </div>
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
