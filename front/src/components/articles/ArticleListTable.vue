<template>
  <table class="w-full border-collapse">
    <!-- 헤더 -->
    <thead>
      <tr class="border-b bg-gray-50 dark:bg-slate-800">
        <th class="p-4 text-left w-16">번호</th>
        <th class="p-4 text-left">제목</th>
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

        <!-- 작성자 -->
        <td class="p-4">
          {{ article.user }}
        </td>

        <!-- 작성시간 -->
        <td class="p-4 text-sm text-gray-500">
          {{ new Date(article.created_at).toLocaleString() }}
        </td>

      </tr>

      <!-- 비어있을 때 -->
      <tr v-if="articles.length === 0">
        <td colspan="4" class="p-6 text-center text-gray-400">
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

const accountStore =useAccountStore()
const API_URL = 'http://127.0.0.1:8000/api/v1'
const articles = ref([]) // 🔥 핵심

onMounted(async () => {
  const res = await axios.get(`${API_URL}/articles/`)
  articles.value = res.data.sort((a, b) => a.id - b.id)
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

</script>
