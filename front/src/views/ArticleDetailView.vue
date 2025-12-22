<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'

/* ========================
   기본 설정
======================== */
const API_URL = 'http://127.0.0.1:8000/api/v1'

const route = useRoute()
const router = useRouter()
const accountStore = useAccountStore()
const commentContent = ref('')

const article = ref(null)
const comments = ref([])

/* ========================
   데이터 로드
======================== */
onMounted(async () => {
  console.log('mounted')
  const res = await axios.get(`${API_URL}/articles/${route.params.id}/`)
  article.value = res.data

  await fetchComments()
})

/* ========================
   computed
======================== */

// 작성자 이름 표시용
const writerName = computed(() => {
  if (!article.value) return ''
  return article.value.user === accountStore.userId
    ? accountStore.userName
    : '다른 사용자'
})

// 내 게시글 여부
const isMyArticle = computed(() => {
  if (!article.value) return false
  return article.value.user === accountStore.userName
})


// 날짜 포맷
const formattedDate = computed(() => {
  if (!article.value) return ''
  return new Date(article.value.created_at).toLocaleString()
})

/* ========================
   actions
======================== */

// 수정 페이지 이동
const goEdit = () => {
  router.push({
    name: 'ArticleEdit',
    params: { id: article.value.id },
  })
}

// 게시글 삭제
const deleteArticle = async () => {
  const ok = confirm('정말 삭제하시겠습니까?')
  if (!ok) return

  try {
    await axios.delete(
      `${API_URL}/articles/${article.value.id}/`,
      {
        headers: {
          Authorization: `Token ${accountStore.token}`,
        },
      }
    )

    alert('삭제되었습니다.')
    router.push({ name: 'ArticleList' })
  } catch (err) {
    console.error(err)
    alert('삭제에 실패했습니다.')
  }
}

const createComment = async () => {
  console.log('clicked')
  console.log(accountStore.token)
  await axios.post(
    `${API_URL}/articles/${route.params.id}/comments/`,
    { content: commentContent.value },
    {
      headers: {
        Authorization: `Token ${accountStore.token}`,
      },
    }
  )
  commentContent.value = ''
  fetchComments()
}

// 댓글 불러오는 함수
const fetchComments = async () => {
  const res = await axios.get(
    `${API_URL}/articles/${route.params.id}/comments/`
  )
  comments.value = res.data
}


</script>

<template>
  <LayoutAuthenticated>
    <h1>🔥 ArticleDetailView</h1>

    <SectionMain>
      <div v-if="article">
        <!-- 제목 -->
        <h1 class="text-2xl font-bold mb-2">
          {{ article.title }}
        </h1>

        <!-- 메타 정보 -->
        <p class="text-gray-500 mb-6">
          {{ writerName }} · {{ formattedDate }}
        </p>

        <!-- 내용 -->
        <div class="whitespace-pre-line mb-6">
          {{ article.content }}
        </div>

        <div class="mt-6">
          <h3 class="font-bold mb-2">댓글</h3>

          <div v-for="comment in comments" :key="comment.id" class="border-b py-2">
            <p class="text-sm text-gray-600">
              {{ comment.user }} ·
              {{ new Date(comment.created_at).toLocaleString() }}
            </p>
            <p>{{ comment.content }}</p>
          </div>
        </div>


        <!-- 내 글일 때만 버튼 표시 -->
        <BaseButtons v-if="isMyArticle">
          <BaseButton
            color="info"
            label="수정"
            @click="goEdit"
          />
          <BaseButton
            color="danger"
            label="삭제"
            @click="deleteArticle"
          />
        </BaseButtons>

        <textarea v-model="commentContent" />
        <button @click="createComment">댓글 작성</button>

      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>
