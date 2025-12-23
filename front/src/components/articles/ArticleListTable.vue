<template>
  <table class="w-full border-collapse">
    <!-- 헤더 -->
    <thead>
      <tr class="border-b bg-gray-50 dark:bg-slate-800">
        <th class="p-4 text-left w-16">번호</th>
        <th class="p-4 text-left">제목</th>
        <th class="p-4 text-left w-32">분류</th>
        <th class="p-4 text-left w-32">작성자</th>
        <th class="p-4 text-left w-40">작성시간</th>
      </tr>
    </thead>


    <!-- 바디 -->
    <tbody>
      <tr
        v-for="(article, index) in articles"
        :key="article.id"
        class="border-b hover:bg-gray-50 dark:hover:bg-slate-700"
      >
        <!-- 번호 -->
        <td class="p-4">
          {{ index + 1 }}
        </td>

        <!-- 제목 (클릭 가능) -->
        <td class="p-4 text-blue-600 hover:underline">
          <RouterLink :to="{ name: 'ArticleDetail', params: { id: article.id } }">
            {{ article.title }}
          </RouterLink>
        </td>

        <!-- 분류 -->
        <td class="p-4">
          <span class="text-sm text-gray-600">{{ getDepartmentName(article) }}</span>
        </td>

        <!-- 작성자 -->
        <td class="p-4">
          <div class="flex items-center gap-2">
            <UserAvatar :src="getAuthorAvatar(article)" :username="getAuthorName(article)" :size="20" />
            <span class="text-sm">{{ getAuthorName(article) }}</span>
          </div>
        </td>

        <!-- 작성시간 -->
        <td class="p-4 text-sm text-gray-500">
          {{ new Date(article.created_at).toLocaleString() }}
        </td>

      </tr>

      <!-- 비어있을 때 -->
      <tr v-if="articles.length === 0">
        <td colspan="5" class="p-6 text-center text-gray-400">
          게시글이 없습니다.
        </td>
      </tr>


    </tbody>
  </table>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'
import UserAvatar from '@/components/UserAvatar.vue'
import { useArticleStore } from '@/stores/articles'

const accountStore = useAccountStore()
const API_URL = 'http://127.0.0.1:8000/api/v1'
const articles = ref([]) // 🔥 핵심

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
    return (typeof deptMap !== 'undefined' && deptMap.value[id]) 
           ? deptMap.value[id] 
           : `부서(${id})`;
  }

  return '미분류';
};

onMounted(async () => {
  // 1. 게시글 목록만 가져옵니다 (부서 목록 가져오던 복잡한 로직은 모두 삭제)
  try {
    const res = await axios.get(`${API_URL}/articles/`)
    
    // 2. 데이터가 배열인지 확인하고 정렬하여 저장
    // (b.id - a.id)로 정렬하면 최신글이 맨 위로 올라옵니다.
    articles.value = Array.isArray(res.data) 
      ? res.data.sort((a, b) => b.id - a.id) 
      : []
      
    console.log('게시글 불러오기 성공:', articles.value)
  } catch (e) {
    articles.value = []
    console.error('Failed to load articles', e)
  }
})

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

const getAuthorName = (article) => {
  if (!article.user) return article.author || ''
  if (typeof article.user === 'object') return article.user.username || article.user.name || ''
  return article.user
}
const getAuthorAvatar = (article) => {
  if (!article.user) return article.author_avatar || article.user_avatar || null
  if (typeof article.user === 'object') return article.user.avatar || article.user.profile_image || null
  return article.user_avatar || article.author_avatar || null
}


</script>
