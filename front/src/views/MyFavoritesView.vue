<template>
    <h1>관심기업</h1>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton title="내 관심기업" :icon="mdiChartTimelineVariant" />

      <div class="grid grid-cols-1 gap-4">
        <CardBox v-for="c in companies" :key="c.id" class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <RouterLink :to="{ name: 'CompanyDetail', params: { id: c.id } }" class="text-lg font-semibold text-blue-600 hover:underline">{{ c.corp_name }}</RouterLink>
              <div class="text-sm text-gray-500">기업코드: {{ c.corp_code || '-' }}</div>
            </div>
            <div>
              <button class="px-3 py-1 border rounded" @click="goDetail(c.id)">상세</button>
            </div>
          </div>
        </CardBox>
        <div v-if="companies.length === 0" class="text-sm text-gray-500">관심 기업이 없습니다.</div>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'
import { useRouter } from 'vue-router'
import { mdiChartTimelineVariant } from '@mdi/js'

const API_BASE = 'http://127.0.0.1:8000'
const companies = ref([])
const router = useRouter()
const accountStore = useAccountStore()

const fetchFavorites = async () => {
  if (!accountStore.token) {
    companies.value = []
    return
  }

  try {
    const r = await axios.get(`${API_BASE}/companies/api/myfavorites/`, { headers: { Authorization: `Token ${accountStore.token}` } })
    companies.value = r.data.companies || []
  } catch (e) {
    console.error('Failed to load favorites', e)
    companies.value = []
  }
}

const goDetail = (id) => router.push({ name: 'CompanyDetail', params: { id } })

onMounted(fetchFavorites)
</script>

<style scoped></style>
