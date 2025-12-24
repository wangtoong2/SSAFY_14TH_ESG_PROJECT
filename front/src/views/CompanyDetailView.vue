<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton title="기업 상세" :icon="mdiAccountMultiple" />

      <div v-if="loading" class="text-gray-600">로딩 중...</div>
      <div v-else-if="error" class="text-red-600">{{ error }}</div>

      <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div>
          <CardBox class="mb-4 flex items-center justify-between">
            <div>
              <h3 class="text-xl font-medium">{{ displayName || '회사명 없음' }}</h3>
              <div class="text-sm text-gray-600">회사 코드: {{ data.corp_code || '-' }} | 주식 코드: {{ data.stock_code || '비상장 기업' }}</div>
            </div>
            <div>
              <button
                class="px-3 py-1 border rounded bg-white hover:bg-gray-50"
                @click="toggleFavorite"
              >
                <span v-if="isFavorited">❤️ 관심기업</span>
                <span v-else>🤍 찜하기</span>
              </button>
            </div>
          </CardBox>
        </div>

        <div>
          <CardBox class="mb-4">
            <h4 class="font-medium">요약</h4>
            <pre class="whitespace-pre-wrap bg-gray-50 p-3 rounded text-sm text-gray-800">{{ prettyOverview }}</pre>
          </CardBox>
        </div>
        <!-- 댓글 섹션 -->
        <div class="lg:col-span-2">
          <CardBox class="mb-4">
            <h4 class="font-medium">댓글</h4>

            <div v-for="comment in comments" :key="comment.id" class="border-b py-3">
              <div class="flex justify-between items-start">
                <div class="flex items-start gap-3">
                  <img :src="comment.user?.avatar || null" alt="avatar" class="w-8 h-8 rounded" v-if="false" />
                  <div>
                    <p class="text-sm text-gray-600">{{ comment.user || '익명' }} · {{ new Date(comment.created_at).toLocaleString() }}</p>
                    <p class="mt-1 whitespace-pre-line">{{ comment.content }}</p>
                    <div class="mt-2 flex items-center gap-2 text-sm">
                      <button @click="toggleCommentLike(comment.id)" class="hover:underline">{{ comment.liked ? '❤️' : '🤍' }}</button>
                      <span>{{ comment.likes_count }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="(comment.user && comment.user === accountStore.userName) || (comment.user && comment.user.username === accountStore.userName)" class="flex gap-2 text-sm">
                  <button class="text-blue-500 hover:underline" @click="editComment(comment)">수정</button>
                  <button class="text-red-500 hover:underline" @click="deleteComment(comment.id)">삭제</button>
                </div>
              </div>
            </div>

            <div class="mt-4">
              <div class="flex items-start gap-3">
                <div class="flex-1">
                  <textarea v-model="commentContent" :disabled="!accountStore.isLogin" class="w-full border rounded p-2" rows="3" placeholder="댓글을 입력하세요"></textarea>

                  <div class="flex justify-end mt-2">
                    <button class="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50" @click="createComment" :disabled="!accountStore.isLogin || !commentContent.trim()">댓글 작성</button>
                    <button v-if="!accountStore.isLogin" class="ml-2 px-4 py-2 border rounded" @click="$router.push({ name: 'login' })">로그인</button>
                  </div>
                </div>
              </div>
            </div>
          </CardBox>
        </div>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import { useAccountStore } from '@/stores/accounts'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import { mdiAccountMultiple } from '@mdi/js'

const route = useRoute()
const id = route.params.id

const API_BASE = 'http://127.0.0.1:8000'
const loading = ref(true)
const error = ref(null)
const data = ref({})
const reason = ref('')

// comments
const accountStore = useAccountStore()
const comments = ref([])
const commentContent = ref('')
const isFavorited = ref(false)

// const prettyOverview = computed(() => {
//   try {
//     return JSON.stringify(data.value.company_overview || data.value.profile?.company_overview || {}, null, 2)
//   } catch (e) {
//     return ''
//   }
// })

const prettyOverview = computed(() => {
  const o =
    data.value.company_overview ||
    data.value.profile?.company_overview ||
    {}

  if (!o || Object.keys(o).length === 0) return '요약 정보가 없습니다.'

  const lines = []

  if (o.region) lines.push(`지역: ${o.region}`)
  if (o.addr || o.adres) lines.push(`주소: ${o.addr || o.adres}`)
  if (o.industry_code) lines.push(`산업 코드: ${o.industry_code}`)
  if (o.est_dt) {
    const y = o.est_dt.slice(0, 4)
    const m = o.est_dt.slice(4, 6)
    const d = o.est_dt.slice(6, 8)
    lines.push(`설립일: ${y}-${m}-${d}`)
  }

  // 비상장/상장 여부 (raw.corp_cls 기준)
  const corpCls = o.raw?.corp_cls
  if (corpCls) {
    const clsMap = {
      Y: '유가증권시장',
      K: '코스닥',
      N: '코넥스',
      E: '비상장',
    }
    lines.push(`기업 구분: ${clsMap[corpCls] || corpCls}`)
  }

  return lines.join('\n')
})


// robust display name for various API shapes
const displayName = computed(() => {
  const d = data.value || {}
  return (
    d.corp_name ||
    ''
  )
})

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    const resp = await axios.get(`${API_BASE}/companies/api/companyprofile/summary/?company_id=${encodeURIComponent(id)}`)
    data.value = resp.data || {}
    // try to extract any recommendation reason if returned inside profile or top-level
    // reason.value = resp.data?.reason || resp.data?.profile?.reason || ''
  } catch (err) {
    console.error(err)
    error.value = err?.response?.data?.error || err.message || 'Failed to load company'
  } finally {
    loading.value = false
  }
})

const fetchFavoriteState = async () => {
  try {
    const r = await axios.get(`${API_BASE}/companies/api/${id}/favorite/`, { headers: { Authorization: `Token ${accountStore.token}` } })
    isFavorited.value = !!r.data.favorited
  } catch (e) {
    console.warn('Failed to fetch favorite state', e)
  }
}

const toggleFavorite = async () => {
  if (!accountStore.token) {
    alert('로그인이 필요합니다.')
    return
  }
  try {
    const r = await axios.post(`${API_BASE}/companies/api/${id}/favorite/`, {}, { headers: { Authorization: `Token ${accountStore.token}` } })
    isFavorited.value = !!r.data.favorited
  } catch (e) {
    console.error('Favorite toggle failed', e)
    alert('처리 실패')
  }
}

onMounted(() => {
  fetchComments()
  fetchFavoriteState()
})

// fetch comments for company
const fetchComments = async () => {
  try {
    const res = await axios.get(`${API_BASE}/companies/api/${id}/comments/`)
    comments.value = res.data
  } catch (e) {
    console.error('Failed to fetch company comments', e)
    comments.value = []
  }
}

const createComment = async () => {
  if (!accountStore.token) {
    alert('로그인이 필요합니다.')
    return
  }
  if (!commentContent.value.trim()) return
  try {
    await axios.post(
      `${API_BASE}/companies/api/${id}/comments/`,
      { content: commentContent.value },
      { headers: { Authorization: `Token ${accountStore.token}` } }
    )
    commentContent.value = ''
    await fetchComments()
  } catch (err) {
    console.error(err)
    alert('댓글 작성 실패')
  }
}

const deleteComment = async (commentId) => {
  const ok = confirm('댓글을 삭제하시겠습니까?')
  if (!ok) return
  await axios.delete(`${API_BASE}/companies/api/comments/${commentId}/`, { headers: { Authorization: `Token ${accountStore.token}` } })
  await fetchComments()
}

const editComment = async (comment) => {
  const newContent = prompt('댓글 수정', comment.content)
  if (!newContent) return
  await axios.patch(
    `${API_BASE}/companies/api/comments/${comment.id}/update/`,
    { content: newContent },
    { headers: { Authorization: `Token ${accountStore.token}` } }
  )
  await fetchComments()
}

const toggleCommentLike = async (commentId) => {
  try {
    const res = await axios.post(
      `${API_BASE}/companies/api/comments/${commentId}/like/`,
      {},
      { headers: { Authorization: `Token ${accountStore.token}` } }
    )
    const target = comments.value.find(c => c.id === commentId)
    if (target) {
      target.likes_count = res.data.likes_count ?? target.likes_count
      target.liked = res.data.liked ?? !target.liked
    }
  } catch (err) {
    console.error(err)
    alert('댓글 좋아요 실패')
  }
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.text-muted { color: #6b7280 }
</style>
