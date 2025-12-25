<script setup>
import { computed, ref, watch } from 'vue'
import axios from 'axios'
import { mdiMagnify } from '@mdi/js'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'
import FormControl from '@/components/FormControl.vue'

const API_BASE = 'http://127.0.0.1:8000'

const isLoading = ref(false)
const errorMessage = ref('')
const companies = ref([])
const query = ref('')

const normalizeText = (s) =>
  (s || '')
    .toString()
    .toLowerCase()
    .replace(/\s+/g, '')
    // keep korean/english/numbers only (drop punctuation/symbols)
    .replace(/[^0-9a-z\u3131-\u318e\uac00-\ud7a3]+/g, '')

const levenshtein = (a, b) => {
  if (a === b) return 0
  if (!a) return b.length
  if (!b) return a.length

  // ensure a is the shorter
  if (a.length > b.length) {
    const tmp = a
    a = b
    b = tmp
  }

  const prev = new Array(a.length + 1)
  const curr = new Array(a.length + 1)
  for (let i = 0; i <= a.length; i++) prev[i] = i

  for (let j = 1; j <= b.length; j++) {
    curr[0] = j
    const bj = b.charCodeAt(j - 1)
    for (let i = 1; i <= a.length; i++) {
      const cost = a.charCodeAt(i - 1) === bj ? 0 : 1
      curr[i] = Math.min(
        prev[i] + 1,
        curr[i - 1] + 1,
        prev[i - 1] + cost
      )
    }
    for (let i = 0; i <= a.length; i++) prev[i] = curr[i]
  }

  return prev[a.length]
}

const filteredCompanies = computed(() => {
  const rawQuery = query.value.trim()
  if (!rawQuery) return []

  const q = normalizeText(rawQuery)
  if (!q) return []

  // cheap pre-score: prioritize prefix/includes first, then fuzzy similarity
  const scored = []

  // For very large datasets, avoid heavy distance on every row.
  // We first take a broader candidate set using a cheap overlap heuristic.
  const all = companies.value
  const maxCandidates = all.length > 3000 ? 400 : all.length
  const qChars = new Set(q.split(''))

  const candidates = all
    .map((c) => {
      const nameRaw = (c?.corp_name || '').toString()
      const name = normalizeText(nameRaw)
      if (!name) return null

      let overlap = 0
      for (const ch of qChars) {
        if (name.includes(ch)) overlap++
      }
      return { c, nameRaw, name, overlap }
    })
    .filter(Boolean)
    .sort((a, b) => b.overlap - a.overlap)
    .slice(0, maxCandidates)

  for (const item of candidates) {
    const name = item.name
    let score = 0

    if (name === q) {
      score = 10
    } else if (name.startsWith(q)) {
      score = 8
    } else if (name.includes(q)) {
      score = 6
    } else {
      const dist = levenshtein(q, name)
      const denom = Math.max(q.length, name.length)
      const sim = denom ? 1 - dist / denom : 0
      score = sim * 5
    }

    scored.push({ company: item.c, score, name: item.name })
  }

  // Keep relevant results only, show best matches first
  const minScore = 2.2
  return scored
    .filter((x) => x.score >= minScore)
    .sort((a, b) => b.score - a.score || a.name.length - b.name.length)
    .slice(0, 50)
    .map((x) => x.company)
})

const fetchCompanies = async (q) => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const res = await axios.get(`${API_BASE}/companies/api/list/`, {
      params: {
        q: q || undefined,
        // for search, request more than the default 500
        limit: q ? 5000 : 500,
      },
    })
    // backend returns { companies: [...] }
    if (Array.isArray(res.data)) {
      companies.value = res.data
    } else if (Array.isArray(res.data?.companies)) {
      companies.value = res.data.companies
    } else {
      companies.value = []
    }
  } catch (err) {
    console.error('기업 목록 로드 실패', err.response?.data || err)
    errorMessage.value = '기업 목록을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

let debounceId = null
watch(
  () => query.value,
  (q) => {
    const trimmed = (q || '').trim()
    if (!trimmed) {
      companies.value = []
      errorMessage.value = ''
      isLoading.value = false
      if (debounceId) clearTimeout(debounceId)
      debounceId = null
      return
    }

    if (debounceId) clearTimeout(debounceId)
    debounceId = setTimeout(() => {
      fetchCompanies(trimmed)
    }, 200)
  }
)
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiMagnify" title="기업 검색하기" main />

      <CardBox>
        <div class="max-w-md">
          <FormControl v-model.trim="query" type="text" placeholder="기업명을 검색하세요" />
        </div>

        <div class="mt-4">
          <div v-if="isLoading" class="text-slate-600">불러오는 중…</div>
          <div v-else-if="errorMessage" class="text-red-600">{{ errorMessage }}</div>

          <div v-else>
            <div v-if="!query" class="text-slate-600">기업명을 입력하면 아래에 목록이 표시됩니다.</div>
            <div v-else-if="companies.length === 0" class="text-slate-600">표시할 기업이 없습니다.</div>
            <div v-else-if="filteredCompanies.length === 0" class="text-slate-600">검색 결과가 없습니다.</div>

            <div v-else class="grid grid-cols-1 gap-2">
              <RouterLink
                v-for="c in filteredCompanies"
                :key="c.id"
                :to="{ name: 'CompanyDetail', params: { id: c.id } }"
                class="block rounded-xl border border-slate-200 bg-white px-4 py-3 hover:bg-sky-50/70 transition"
              >
                <div class="flex items-center justify-between gap-4">
                  <div class="min-w-0">
                    <div class="font-semibold text-slate-900 truncate">{{ c.corp_name }}</div>
                    <div class="mt-1 text-sm text-slate-600">
                      <span v-if="c.corp_code">기업코드: {{ c.corp_code }}</span>
                      <span v-else>기업코드: -</span>
                    </div>
                  </div>
                  <div class="text-sm text-primary whitespace-nowrap">자세히</div>
                </div>
              </RouterLink>
            </div>
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
