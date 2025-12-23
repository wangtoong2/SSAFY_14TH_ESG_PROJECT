<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton
        :icon="mdiBallotOutline"
        title="게시글 작성"
        main
      />

      <form @submit.prevent="createArticle" class="space-y-6">

        <FormField label="제목">
          <FormControl
            v-model.trim="form.title"
            type="text"
            placeholder="제목을 입력하세요."
          />
        </FormField>

        <FormField label="분류">
          <FormControl
            v-model="form.department"
            :options="selectOptions"
          />
        </FormField>

        <FormField label="내용">
          <FormControl
            v-model.trim="form.content"
            type="textarea"
            placeholder="내용을 입력하세요."
          />
        </FormField>

        <BaseButtons>
          <BaseButton
            type="submit"
            color="info"
            label="Submit"
          />
          <BaseButton
            type="reset"
            color="info"
            outline
            label="Reset"
          />
        </BaseButtons>

      </form>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { mdiBallotOutline } from '@mdi/js'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import { useAccountStore } from '@/stores/accounts'

const accountStore = useAccountStore()
const router = useRouter()
const API_URL = 'http://127.0.0.1:8000/api/v1'


const selectOptions = [
  { id: 1, label: 'Business development' },
  { id: 2, label: 'Marketing' },
  { id: 3, label: 'Sales' },
]

const form = reactive({
  title: '',
  content: '',
  department: selectOptions[0],
})

const createArticle = async () => {
  const token = accountStore.token
  console.log('🔥 createArticle 호출됨')

  if (!form.title || !form.content) {
    alert('제목과 내용을 입력하세요.')
    return
  }

  const payload = {
    title: form.title,
    content: form.content,
    department: form.department ? form.department.id : null, 
  }

  console.log('최종 전송 데이터(payload):', payload)

  console.log('payload:', payload)
  console.log('token:', token)

  try {
    await axios.post(
      `${API_URL}/articles/`,
      payload,
      {
        headers: {
          Authorization: `Token ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )

    console.log('✅ 게시글 생성 성공')
    router.push({ name: 'ArticleList' })

  } catch (err) {
    console.error('❌ 게시글 생성 실패:', err.response?.data || err)
    alert('게시글 등록에 실패했습니다.')
  }
}
</script>
