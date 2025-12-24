<script setup>
import { mdiTableBorder } from '@mdi/js'
import { ref, reactive } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'

import ArticleListTable from '@/components/articles/ArticleListTable.vue'
import BaseButton from '@/components/BaseButton.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'

const accountStore = useAccountStore()
const API_URL = 'http://127.0.0.1:8000/api/v1'

const showCreate = ref(false)
const tableRef = ref(null)

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

const resetForm = () => {
  form.title = ''
  form.content = ''
  form.department = selectOptions[0]
}

const createArticle = async () => {
  const token = accountStore.token
  if (!form.title || !form.content) {
    alert('제목과 내용을 입력하세요.')
    return
  }

  const payload = {
    title: form.title,
    content: form.content,
    department: form.department ? form.department.id : null,
  }

  try {
    await axios.post(`${API_URL}/articles/`, payload, {
      headers: {
        Authorization: `Token ${token}`,
        'Content-Type': 'application/json',
      },
    })

    // refresh table via exposed method
    if (tableRef.value && tableRef.value.fetchArticles) {
      await tableRef.value.fetchArticles()
    } else {
      window.location.reload()
    }

    resetForm()
    showCreate.value = false
  } catch (err) {
    console.error('게시글 생성 실패', err)
    alert('게시글 등록에 실패했습니다.')
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton
        :icon="mdiTableBorder"
        title="게시글 목록"
        main
      >
        <BaseButton label="글작성" color="info" @click="showCreate = true" />
      </SectionTitleLineWithButton>

      <!-- inline create form -->
      <CardBox v-if="showCreate" class="mb-6">
        <form @submit.prevent="createArticle" class="space-y-4">
          <FormField label="제목">
            <FormControl v-model.trim="form.title" type="text" placeholder="제목을 입력하세요." />
          </FormField>

          <FormField label="분류">
            <FormControl v-model="form.department" :options="selectOptions" />
          </FormField>

          <FormField label="내용">
            <FormControl v-model.trim="form.content" type="textarea" placeholder="내용을 입력하세요." />
          </FormField>

          <BaseButtons>
            <BaseButton type="submit" color="info" label="등록" />
            <BaseButton type="button" color="whiteDark" outline @click="showCreate = false; resetForm()" label="취소" />
          </BaseButtons>
        </form>
      </CardBox>

      <CardBox class="mb-6" has-table>
        <!-- 자동으로 호출 -->
        <ArticleListTable ref="tableRef" />
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
