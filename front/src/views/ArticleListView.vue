<script setup>
import { mdiTableBorder } from '@mdi/js'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'

import ArticleListTable from '@/components/articles/ArticleListTable.vue'
import BaseButton from '@/components/BaseButton.vue'
import FormControl from '@/components/FormControl.vue'

const router = useRouter()
const tableRef = ref(null)
const searchTitle = ref('')

const goCreate = () => {
  router.push({ name: 'ArticleCreate' })
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
        <div class="flex items-center gap-3">
          <div class="w-56">
            <FormControl v-model.trim="searchTitle" type="text" placeholder="제목 검색" />
          </div>
          <BaseButton label="글작성" color="info" @click="goCreate" />
        </div>
      </SectionTitleLineWithButton>

      <CardBox class="mb-6" has-table>
        <!-- 자동으로 호출 -->
        <ArticleListTable ref="tableRef" :search-query="searchTitle" />
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
