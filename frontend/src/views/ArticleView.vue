<template>
  <div>
    <h1>게시판입니다</h1>
    <RouterLink :to="{name:'CreateView'}">
      [CREATE]
    </RouterLink>
    <ArticleList />
  </div>
</template>

<script setup>
  import { onMounted } from 'vue';
  import { useArticleStore } from '@/stores/articles';
  import { RouterLink } from 'vue-router';
  import ArticleList from '@/components/ArticleList.vue';

  const store = useArticleStore()

  onMounted(() =>{
    store.getArticles()
  })
</script>

<style scoped>

</style>