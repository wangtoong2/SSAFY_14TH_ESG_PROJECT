<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { mdiFileDocumentOutline } from '@mdi/js'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'

import { useAccountStore } from '@/stores/accounts'

const accountStore = useAccountStore()
const API_URL = 'http://127.0.0.1:8000/api/v1'

const isLoading = ref(false)
const errorMessage = ref('')
const articles = ref([])

const fetchMyArticles = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const res = await axios.get(`${API_URL}/articles/me/`, {
      headers: {
        Authorization: `Token ${accountStore.token}`,
      },
    })

    articles.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.error('내가 작성한 글 조회 실패', err.response?.data || err)
    errorMessage.value = '내가 작성한 글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchMyArticles()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiFileDocumentOutline" title="내가 작성한 글" main />

      <CardBox>
        <div v-if="isLoading" class="text-slate-600">불러오는 중…</div>
        <div v-else-if="errorMessage" class="text-red-600">{{ errorMessage }}</div>

        <div v-else>
          <div v-if="articles.length === 0" class="text-slate-600">작성한 게시글이 없습니다.</div>

          <div v-else class="divide-y divide-slate-100">
            <RouterLink
              v-for="a in articles"
              :key="a.id"
              :to="{ name: 'ArticleDetail', params: { id: a.id } }"
              class="block py-4 hover:bg-sky-50/70 rounded-xl px-2 transition"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <div class="font-semibold text-slate-900 truncate">{{ a.title }}</div>
                  <div class="mt-1 text-sm text-slate-600">
                    <span v-if="a.department_name">분류: {{ a.department_name }}</span>
                    <span v-else>분류: -</span>
                    <span class="mx-2">·</span>
                    <span>작성일: {{ a.created_at }}</span>
                  </div>
                </div>
                <div class="text-sm text-primary whitespace-nowrap">보기</div>
              </div>
            </RouterLink>
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
