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

const article = ref(null)

const comments = ref([])
const commentContent = ref('')

/* ========================
   데이터 로드
======================== */
onMounted(async () => {
  console.log('mounted')
  const res = await axios.get(`${API_URL}/articles/${route.params.id}/`)
  article.value = res.data

  await fetchComments()
})


// const writerName = computed(() => {
//   if (!article.value) return ''
//   return article.value.user
// })

const writerName = computed(() => article.value?.user ?? '')



// 내 게시글 여부
const isMyArticle = computed(() => {
  if (!article.value || !accountStore.userName) return false
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

// 좋아요 토글 함수 추가
const toggleArticleLike = async () => {
  try {
  const res = await axios.post(
    `${API_URL}/articles/${article.value.id}/like/`,
    {},
    {
      headers: {
        Authorization: `Token ${accountStore.token}`,
      },
    }
  )
  article.value.likes_count = res.data.likes_count
  article.value.liked = res.data.liked
} catch (err) {
    console.error(err)
    alert('좋아요 처리 실패')
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
      `${API_URL}/articles/${route.params.id}/comments/`,
      { content: commentContent.value },
      {
        headers: {
          Authorization: `Token ${accountStore.token}`,
        },
      }
    )

    commentContent.value = ''
    await fetchComments()
  } catch (err) {
    console.error(err)
    alert('댓글 작성 실패')
  }
}


// 댓글 불러오는 함수
const fetchComments = async () => {
  const res = await axios.get(
    `${API_URL}/articles/${route.params.id}/comments/`
  )
  comments.value = res.data
}

// 댓글 삭제 함수
const deleteComment = async (commentId) => {
  const ok = confirm('댓글을 삭제하시겠습니까?')
  if (!ok) return

  await axios.delete(
    `${API_URL}/articles/comments/${commentId}/`,
    {
      headers: {
        Authorization: `Token ${accountStore.token}`,
      },
    }
  )

  await fetchComments()
}

const isMyComment = (comment) => {
  return comment.user === accountStore.userName
}


// 댓글 수정 함수
const editComment = async (comment) => {
  const newContent = prompt('댓글 수정', comment.content)
  if (!newContent) return

  await axios.patch(
    `${API_URL}/articles/comments/${comment.id}/update/`,
    { content: newContent },
    {
      headers: {
        Authorization: `Token ${accountStore.token}`,
      },
    }
  )

  await fetchComments()
}

const toggleCommentLike = async (commentId) => {
  try {
    const res = await axios.post(
      `${API_URL}/articles/comments/${commentId}/like/`,
      {},
      {
        headers: {
          Authorization: `Token ${accountStore.token}`,
        },
      }
    )

    // 좋아요 수 즉시 반영
    const target = comments.value.find(c => c.id === commentId)
    if (target) {
      target.likes_count = res.data.likes_count
      target.liked = res.data.liked
    }

  } catch (err) {
    console.error(err)
    alert('댓글 좋아요 실패')
  }
}



</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <div v-if="article" class="space-y-6">

        <!-- 제목 -->
        <h1 class="text-2xl font-bold">
          {{ article.title }}
        </h1>

        <!-- 메타 정보 -->
        <p class="text-sm text-gray-500">
          {{ writerName }} · {{ formattedDate }}
        </p>

        <!-- 내용 -->
        <div class="whitespace-pre-line border-t pt-4">
          {{ article.content }}
        </div>

        <!-- 게시글 좋아요 -->
        <div class="flex items-center gap-2 mb-6">
          <button 
            class="px-3 py-1 border rounded hover:bg-gray-100"
            @click="toggleArticleLike">
              {{ article.liked ? '❤️' : '🤍' }}
          </button>
          <span>{{ article.likes_count }}</span>
        </div>



        <!-- 게시글 관리 버튼 (내 글일 때만) -->
        <BaseButtons v-if="isMyArticle" class="mt-4">
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

        <!-- ======================
            댓글 영역
        ====================== -->
        <div class="mt-8">
          <h3 class="font-bold mb-4">댓글</h3>

          <!-- 댓글 목록 -->
          <div
            v-for="comment in comments"
            :key="comment.id"
            class="border-b py-3"
          >
            <!-- 상단: 작성자 / 시간 / 액션 -->
            <div class="flex justify-between items-center">
              <p class="text-sm text-gray-600">
                {{ comment.user }} ·
                {{ new Date(comment.created_at).toLocaleString() }}
              </p>

              <!-- 내 댓글일 때만 액션 -->
              <div v-if="isMyComment(comment)" class="flex gap-2 text-sm">
                <button
                  class="text-blue-500 hover:underline"
                  @click="editComment(comment)"
                >
                  수정
                </button>

                <button
                  class="text-red-500 hover:underline"
                  @click="deleteComment(comment.id)"
                >
                  삭제
                </button>
              </div>
            </div>

            <!-- 댓글 내용 -->
            <p class="mt-1 whitespace-pre-line">
              {{ comment.content }}
            </p>

            <!-- (확장용) 댓글 좋아요 자리 -->
            
            <div class="mt-2 flex items-center gap-2 text-sm">
              <button @click="toggleCommentLike(comment.id)">
                {{ comment.liked ? '❤️' : '🤍' }}
              </button>
              <span>{{ comment.likes_count }}</span>
            </div>

           
          </div>

          <!-- 댓글 작성 -->
          <div class="mt-4 space-y-2">
            <textarea
              v-model="commentContent"
              class="w-full border rounded p-2"
              rows="3"
              placeholder="댓글을 입력하세요"
            />

            <button
              class="px-4 py-2 bg-blue-500 text-white rounded"
              @click="createComment"
            >
              댓글 작성
            </button>
          </div>
        </div>


      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

