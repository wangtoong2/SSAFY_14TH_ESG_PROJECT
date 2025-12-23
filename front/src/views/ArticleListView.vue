<script setup>
import { mdiTableBorder } from '@mdi/js'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import CardBox from '@/components/CardBox.vue'

import ArticleListTable from '@/components/articles/ArticleListTable.vue'
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton
        :icon="mdiTableBorder"
        title="게시글 목록"
        main
      />

      <CardBox class="mb-6" has-table>
        <!-- 자동으로 호출 -->
        <ArticleListTable />
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
