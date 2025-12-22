<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton
        title="게시글 수정"
        main
      />

      <form @submit.prevent="updateArticle" class="space-y-6">
        <FormField label="제목">
          <FormControl
            v-model.trim="form.title"
            type="text"
          />
        </FormField>

        <FormField label="내용">
          <FormControl
            v-model.trim="form.content"
            type="textarea"
          />
        </FormField>

        <BaseButtons>
          <BaseButton type="submit" color="info" label="수정" />
          <BaseButton
            outline
            label="취소"
            @click="router.back()"
          />
        </BaseButtons>
      </form>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import { useAccountStore } from '@/stores/accounts'

const accountStore = useAccountStore()

const API_URL = 'http://127.0.0.1:8000/api/v1'

const route = useRoute()
const router = useRouter()

const form = reactive({
  title: '',
  content: '',
})

onMounted(async () => {
  const res = await axios.get(`${API_URL}/articles/${route.params.id}/`)
  form.title = res.data.title
  form.content = res.data.content
})

const updateArticle = async () => {
  await axios.put(
    `${API_URL}/articles/${route.params.id}/`,
    {
      title: form.title,
      content: form.content,
    },
    {
      headers: {
            Authorization: `Token ${accountStore.token}`,
            'Content-Type': 'application/json',
          },
    },
  )

  router.push({ name: 'ArticleDetail', params: { id: route.params.id } })
}
</script>
