<template>
  <div class="card-box p-4 bg-white dark:bg-slate-900/70 border border-gray-200 dark:border-slate-800 rounded-lg">
    <h3 class="text-lg font-semibold mb-3">게시글 목록</h3>

    <div v-if="loading">로딩 중...</div>
    <div v-else>
      <ul class="space-y-3">
        <li
          v-for="item in articles"
          :key="item.id"
          class="p-3 border rounded hover:bg-gray-50 cursor-pointer"
          @click="openDetail(item)"
        >
          <div class="flex items-start justify-between">
            <div>
              <div class="font-medium">{{ item.title }}</div>
              <div class="text-sm text-gray-500 truncate">{{ item.summary }}</div>
            </div>
            <div class="ml-4 flex flex-col items-end">
              <div class="flex items-center gap-2 text-sm text-gray-600">
                <UserAvatar :src="item.authorAvatar" :username="item.authorName" :size="20" />
                <span>{{ item.authorName }}</span>
              </div>
            </div>
          </div>
        </li>
      </ul>

      <div v-if="!articles.length" class="text-sm text-gray-500 mt-3">게시글이 없습니다.</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/UserAvatar.vue'

const articles = ref([])
const loading = ref(false)
const accountStore = useAccountStore()
const router = useRouter()

// 부서 매핑용 (필요시 사용)
const deptMap = ref({})

// 데이터 정규화 함수
const normalizeList = (list) => {
  return list.map((a) => {
    const title = a.title ?? a.subject ?? a.name ?? 'Untitled'
    const summary =
      a.summary ??
      a.excerpt ??
      (typeof a.content === 'string' ? a.content.slice(0, 200) : '')

    let authorName = ''
    let authorAvatar = null
    if (a.user) {
      if (typeof a.user === 'object') {
        authorName = a.user.username || a.user.name || ''
        authorAvatar = a.user.avatar || a.user.profile_image || null
      } else {
        authorName = a.user
        authorAvatar = a.user_avatar || a.author_avatar || null
      }
    } else {
      authorName = a.author || ''
      authorAvatar = a.author_avatar || null
    }

    let departmentName = a.department_name || '' // 백엔드에서 준 이름 우선
    if (!departmentName && a.department) {
      if (typeof a.department === 'object') {
        departmentName = a.department.name || a.department.title || ''
      } else {
        departmentName = `부서(${a.department})`
      }
    }

    return {
      id: a.id,
      title,
      summary,
      raw: a,
      authorName,
      authorAvatar,
      departmentName,
    }
  })
}

// ✅ 게시글 가져오기 함수 (중복 제거 및 단일화)
const fetchArticles = async () => {
  loading.value = true
  try {
    // 404 에러를 방지하기 위해 확실한 API 주소 하나만 호출합니다.
    const API_URL = 'http://127.0.0.1:8000/api/v1/articles/'
    const response = await axios.get(API_URL)
    const data = response.data

    if (Array.isArray(data)) {
      articles.value = normalizeList(data)
    } else if (data?.results && Array.isArray(data.results)) {
      articles.value = normalizeList(data.results)
    } else {
      articles.value = []
    }
  } catch (e) {
    console.error('Failed to load articles:', e)
    articles.value = []
  } finally {
    loading.value = false
  }
}

const openDetail = (item) => {
  if (!accountStore.isLogin) {
    alert('상세 보기 전 로그인이 필요합니다.')
    router.push({ name: 'login' })
    return
  }
  router.push({ name: 'ArticleDetail', params: { id: item.id } })
}

onMounted(fetchArticles)
</script>
