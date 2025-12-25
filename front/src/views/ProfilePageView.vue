<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import { mdiAccountCircle } from '@mdi/js'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'

import { useAccountStore } from '@/stores/accounts'

const accountStore = useAccountStore()
const API_URL = 'http://127.0.0.1:8000/api/v1'

const isLoading = ref(false)
const errorMessage = ref('')

const myArticles = ref([])
const myComments = ref([])

const fetchAll = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const [articlesRes, commentsRes] = await Promise.all([
      axios.get(`${API_URL}/articles/me/`, {
        headers: { Authorization: `Token ${accountStore.token}` },
      }),
      axios.get(`${API_URL}/articles/me/comments/`, {
        headers: { Authorization: `Token ${accountStore.token}` },
      }),
    ])

    myArticles.value = Array.isArray(articlesRes.data) ? articlesRes.data : []
    myComments.value = Array.isArray(commentsRes.data) ? commentsRes.data : []
  } catch (err) {
    console.error('내 프로필 데이터 조회 실패', err?.response?.data || err)
    errorMessage.value = '내 프로필 정보를 불러오지 못했습니다.'
    myArticles.value = []
    myComments.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAll()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiAccountCircle" title="프로필" main />

      <CardBox class="mb-6">
        <div class="text-slate-900 dark:text-slate-100 font-semibold">
          {{ accountStore.nickname || accountStore.userName }}
        </div>
        <div class="mt-1 text-sm text-slate-600 dark:text-slate-300">
          @{{ accountStore.userName }}
        </div>
      </CardBox>

      <CardBox>
        <div v-if="isLoading" class="text-slate-600 dark:text-slate-300">불러오는 중…</div>
        <div v-else-if="errorMessage" class="text-red-600">{{ errorMessage }}</div>

        <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div>
            <div class="mb-3 text-slate-900 dark:text-slate-100 font-semibold">작성한 게시글</div>

            <div v-if="myArticles.length === 0" class="text-slate-600 dark:text-slate-300">작성한 게시글이 없습니다.</div>

            <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
              <RouterLink
                v-for="a in myArticles"
                :key="a.id"
                :to="{ name: 'ArticleDetail', params: { id: a.id } }"
                class="block py-3 hover:bg-sky-50/70 dark:hover:bg-slate-800/40 rounded-xl px-2 transition"
              >
                <div class="font-semibold text-slate-900 dark:text-slate-100 truncate">{{ a.title }}</div>
                <div class="mt-1 text-sm text-slate-600 dark:text-slate-300">
                  <span v-if="a.department_name">분류: {{ a.department_name }}</span>
                  <span v-else>분류: -</span>
                </div>
              </RouterLink>
            </div>
          </div>

          <div>
            <div class="mb-3 text-slate-900 dark:text-slate-100 font-semibold">작성한 댓글</div>

            <div v-if="myComments.length === 0" class="text-slate-600 dark:text-slate-300">작성한 댓글이 없습니다.</div>

            <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
              <RouterLink
                v-for="c in myComments"
                :key="c.id"
                :to="{ name: 'ArticleDetail', params: { id: c.article_id } }"
                class="block py-3 hover:bg-sky-50/70 dark:hover:bg-slate-800/40 rounded-xl px-2 transition"
              >
                <div class="text-sm text-slate-600 dark:text-slate-300">
                  <span class="font-semibold text-slate-800 dark:text-slate-100">{{ c.article_title }}</span>
                  <span class="mx-2">·</span>
                  <span v-if="c.department_name">분류: {{ c.department_name }}</span>
                  <span v-else>분류: -</span>
                </div>
                <div class="mt-2 text-slate-900 dark:text-slate-100 break-words">{{ c.content }}</div>
              </RouterLink>
            </div>
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
