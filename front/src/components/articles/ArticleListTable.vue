<template>
  <div class="overflow-x-auto">
    <div class="overflow-hidden rounded-2xl border border-slate-200/70 dark:border-slate-700/60">
      <table class="w-full border-collapse text-sm">
        <!-- 헤더 -->
        <thead>
          <tr class="border-b border-slate-200/70 bg-sky-50/70 text-slate-700 dark:border-slate-700/60 dark:bg-slate-800 dark:text-slate-200">
            <th class="p-4 text-left w-16 font-semibold">번호</th>
            <th class="p-4 text-left font-semibold">제목</th>
            <th class="p-4 text-left w-40 font-semibold">분류</th>
            <th class="p-4 text-left w-40 font-semibold">작성자</th>
            <th class="p-4 text-left w-48 font-semibold">작성시간</th>
          </tr>
        </thead>

        <!-- 바디 -->
        <tbody>
          <tr
            v-for="(article, index) in filteredArticles"
            :key="article.id"
            class="border-b border-slate-200/70 text-slate-700 transition-colors odd:bg-white even:bg-slate-50/60 hover:bg-sky-50/70 dark:border-slate-700/60 dark:text-slate-200 dark:odd:bg-slate-900/20 dark:even:bg-slate-900/40 dark:hover:bg-slate-700/50"
          >
            <!-- 번호 -->
            <td class="p-4">
              <span class="inline-flex h-7 w-7 items-center justify-center rounded-full bg-white text-slate-600 dark:bg-slate-800 dark:text-slate-200">
                {{ index + 1 }}
              </span>
            </td>

            <!-- 제목 (클릭 가능) -->
            <td class="p-4">
              <RouterLink
                :to="{ name: 'ArticleDetail', params: { id: article.id } }"
                class="font-semibold text-slate-900 hover:underline dark:text-slate-100"
              >
                {{ article.title }}
              </RouterLink>
            </td>

            <!-- 분류 -->
            <td class="p-4">
              <span class="inline-flex items-center rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                {{ getDepartmentName(article) }}
              </span>
            </td>

            <!-- 작성자 -->
            <td class="p-4">
              <RouterLink
                v-if="getAuthorUsername(article)"
                :to="{ name: 'UserProfile', params: { username: getAuthorUsername(article) } }"
                class="flex items-center gap-2"
              >
                <UserAvatar :src="getAuthorAvatar(article)" :username="getAuthorUsername(article)" :size="20" />
                <span class="text-sm font-medium hover:underline">{{ getAuthorDisplayName(article) }}</span>
              </RouterLink>
              <div v-else class="flex items-center gap-2">
                <UserAvatar :src="getAuthorAvatar(article)" :username="getAuthorDisplayName(article)" :size="20" />
                <span class="text-sm font-medium">{{ getAuthorDisplayName(article) }}</span>
              </div>
            </td>

            <!-- 작성시간 -->
            <td class="p-4 text-xs text-slate-500 dark:text-slate-300">
              {{ new Date(article.created_at).toLocaleString() }}
            </td>
          </tr>

          <!-- 비어있을 때 -->
          <tr v-if="filteredArticles.length === 0">
            <td colspan="5" class="p-10 text-center text-slate-400 dark:text-slate-400">
              {{ searchQueryTrimmed ? '검색 결과가 없습니다.' : '게시글이 없습니다.' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'
import UserAvatar from '@/components/UserAvatar.vue'
import { useArticleStore } from '@/stores/articles'

const props = defineProps({
  searchQuery: { type: String, default: '' },
})

const accountStore = useAccountStore()
const API_URL = 'http://127.0.0.1:8000/api/v1'
const articles = ref([]) // 🔥 핵심

const searchQueryTrimmed = computed(() => (props.searchQuery || '').trim().toLowerCase())
const filteredArticles = computed(() => {
  const q = searchQueryTrimmed.value
  if (!q) return articles.value
  return articles.value.filter((a) => String(a?.title || '').toLowerCase().includes(q))
})

// departments mapping
const departments = ref([]) // raw list
const deptMap = ref({}) // id -> label

// try multiple endpoints, return data or null
// const tryFetch = async (urls) => {
//   for (const url of urls) {
//     try {
//       const r = await axios.get(url)
//       if (r && r.status >= 200 && r.status < 300) return r.data
//     } catch (e) {
//       // ignore and try next
//     }
//   }
//   return null
// }

// ArticleListTable.vue 의 getDepartmentName 함수 수정
// ArticleListTable.vue 의 script setup 내부

const getDepartmentName = (article) => {
  // 1. 백엔드 시리얼라이저가 준 이름이 있으면 바로 사용
  if (article.department_name) {
    return article.department_name;
  }

  // 2. department 필드가 객체인 경우 (예: {id: 1, name: 'Marketing'})
  if (article.department && typeof article.department === 'object') {
    return article.department.name || article.department.title || '';
  }

  // 3. department 필드가 ID(숫자)인 경우
  if (article.department) {
    const id = String(article.department);
    // 상단에 선언된 deptMap이 있는지 확인하고 있으면 매핑, 없으면 숫자 표시
    return (typeof deptMap.value !== 'undefined' && deptMap.value[id]) 
           ? deptMap.value[id] 
           : `부서(${id})`;
  }

  return '미분류';
};

const fetchArticles = async () => {
  try {
    const res = await axios.get(`${API_URL}/articles/`)
    articles.value = Array.isArray(res.data)
      ? res.data.sort((a, b) => b.id - a.id)
      : []
    // DEBUG: 게시글 목록 로드 성공 확인용 로그
    // console.log('게시글 불러오기 성공:', articles.value)
  } catch (e) {
    articles.value = []
    console.error('Failed to load articles', e)
  }
}

onMounted(fetchArticles)

// expose for parent refresh
defineExpose({ fetchArticles })

const deleteArticle = async (id) => {
  const ok = confirm('정말 삭제하시겠습니까?')
  if (!ok) return

  try {
    await axios.delete(
      `${API_URL}/articles/${id}/`,
      {
        headers: {
          Authorization: `Token ${accountStore.token}`,
        },
      }
    )

    // ✅ 삭제 후 목록에서 즉시 제거 (UX 핵심)
    articles.value = articles.value.filter(article => article.id !== id)

    alert('삭제되었습니다.')
  } catch (err) {
    console.error('삭제 실패:', err.response?.data || err)
    alert('삭제에 실패했습니다.')
  }
}

const isMyArticle = (article) => {
  if (!article.user) return false

  // case 1: user가 문자열인 경우
  if (typeof article.user === 'string') {
    return article.user === accountStore.userName
  }

  // case 2: user가 객체인 경우
  if (typeof article.user === 'object') {
    return article.user.username === accountStore.userName
  }

  return false
}

const getAuthorUsername = (article) => {
  if (!article?.user) return ''
  if (typeof article.user === 'object') return article.user.username || ''
  return String(article.user || '')
}

const getAuthorDisplayName = (article) => {
  if (!article?.user) return article.author || ''
  if (typeof article.user === 'object') return article.user.nickname || article.user.username || article.user.name || ''
  return String(article.user || '')
}

const getAuthorAvatar = (article) => {
  if (!article.user) return article.author_avatar || article.user_avatar || null
  if (typeof article.user === 'object') return article.user.avatar || article.user.profile_image || null
  return article.user_avatar || article.author_avatar || null
}


</script>
