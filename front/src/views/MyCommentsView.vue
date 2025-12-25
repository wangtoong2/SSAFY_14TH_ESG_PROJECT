<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { mdiCommentTextOutline } from '@mdi/js'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'

import { useAccountStore } from '@/stores/accounts'

const accountStore = useAccountStore()
const API_URL = 'http://127.0.0.1:8000/api/v1'

const isLoading = ref(false)
const errorMessage = ref('')
const comments = ref([])

const fetchMyComments = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const res = await axios.get(`${API_URL}/articles/me/comments/`, {
      headers: {
        Authorization: `Token ${accountStore.token}`,
      },
    })

    comments.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.error('내가 작성한 댓글 조회 실패', err.response?.data || err)
    errorMessage.value = '내가 작성한 댓글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchMyComments()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiCommentTextOutline" title="내가 작성한 댓글" main />

      <CardBox>
        <div v-if="isLoading" class="text-slate-600">불러오는 중…</div>
        <div v-else-if="errorMessage" class="text-red-600">{{ errorMessage }}</div>

        <div v-else>
          <div v-if="comments.length === 0" class="text-slate-600">작성한 댓글이 없습니다.</div>

          <div v-else class="divide-y divide-slate-100">
            <RouterLink
              v-for="c in comments"
              :key="c.id"
              :to="{ name: 'ArticleDetail', params: { id: c.article_id } }"
              class="block py-4 hover:bg-sky-50/70 rounded-xl px-2 transition"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <div class="text-sm text-slate-600">
                    <span class="font-semibold text-slate-800">{{ c.article_title }}</span>
                    <span class="mx-2">·</span>
                    <span v-if="c.department_name">분류: {{ c.department_name }}</span>
                    <span v-else>분류: -</span>
                  </div>
                  <div class="mt-2 text-slate-900 break-words">{{ c.content }}</div>
                  <div class="mt-2 text-xs text-slate-500">작성일: {{ c.created_at }}</div>
                </div>
                <div class="text-sm text-primary whitespace-nowrap">이동</div>
              </div>
            </RouterLink>
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
