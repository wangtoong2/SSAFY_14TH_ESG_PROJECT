<template>
  <div>
    <h3>Article List</h3>
    <ArticleListItem 
    v-for="article in stroe.articles"
    :key="article.id"
    :article="article"/>

  </div>
</template>

<script setup>
import ArticleListItem from '@/components/ArticleListItem.vue';

import { useArticleStore } from '@/stores/articles';
const stroe = useArticleStore()
</script>

<style scoped>

</style>