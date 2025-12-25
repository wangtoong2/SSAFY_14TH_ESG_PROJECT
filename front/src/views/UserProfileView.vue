<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import axios from 'axios'
import { mdiAccountCircle } from '@mdi/js'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'
import UserAvatar from '@/components/UserAvatar.vue'

import { useAccountStore } from '@/stores/accounts'

const route = useRoute()
const accountStore = useAccountStore()

const API_URL = 'http://127.0.0.1:8000/api/v1'

const username = computed(() => String(route.params.username || ''))

const isLoading = ref(false)
const errorMessage = ref('')

const articles = ref([])
const comments = ref([])

const profileUser = computed(() => {
  const candidates = []
  for (const a of articles.value || []) {
    if (a?.user && typeof a.user === 'object') candidates.push(a.user)
  }
  for (const c of comments.value || []) {
    if (c?.user && typeof c.user === 'object') candidates.push(c.user)
  }

  const u = candidates.find((x) => x?.username) || null
  return {
    username: u?.username || username.value,
    nickname: u?.nickname || '',
    avatar: u?.avatar || u?.profile_image || null,
  }
})

const displayName = computed(() => profileUser.value.nickname || profileUser.value.username)

const authHeaderOrEmpty = () => {
  if (!accountStore?.token) return {}
  return { Authorization: `Token ${accountStore.token}` }
}

const fetchAll = async () => {
  if (!username.value) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    const [articlesRes, commentsRes] = await Promise.all([
      axios.get(`${API_URL}/articles/user/${encodeURIComponent(username.value)}/`, {
        headers: authHeaderOrEmpty(),
      }),
      axios.get(`${API_URL}/articles/user/${encodeURIComponent(username.value)}/comments/`, {
        headers: authHeaderOrEmpty(),
      }),
    ])

    articles.value = Array.isArray(articlesRes.data) ? articlesRes.data : []
    comments.value = Array.isArray(commentsRes.data) ? commentsRes.data : []
  } catch (err) {
    console.error('유저 프로필 조회 실패', err?.response?.data || err)
    errorMessage.value = '사용자 프로필을 불러오지 못했습니다.'
    articles.value = []
    comments.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchAll)
watch(username, () => fetchAll())
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiAccountCircle" :title="displayName" main />

      <CardBox class="mb-6">
        <div class="flex items-center gap-4">
          <UserAvatar :src="profileUser.avatar" :username="profileUser.username" :size="56" />
          <div class="min-w-0">
            <div class="text-slate-900 dark:text-slate-100 font-semibold truncate">
              {{ displayName }}
            </div>
          </div>
        </div>
      </CardBox>

      <CardBox>
        <div v-if="isLoading" class="text-slate-600 dark:text-slate-300">불러오는 중…</div>
        <div v-else-if="errorMessage" class="text-red-600">{{ errorMessage }}</div>

        <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div>
            <div class="mb-3 text-slate-900 dark:text-slate-100 font-semibold">작성한 게시글</div>

            <div v-if="articles.length === 0" class="text-slate-600 dark:text-slate-300">작성한 게시글이 없습니다.</div>

            <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
              <RouterLink
                v-for="a in articles"
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

            <div v-if="comments.length === 0" class="text-slate-600 dark:text-slate-300">작성한 댓글이 없습니다.</div>

            <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
              <RouterLink
                v-for="c in comments"
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
