<template>
  <div>
    <p>id : {{ article.id }}</p>
    <br>
    <p>title : {{ article.title}}</p>
    <br>
    <p>content : {{ article.content }}</p>
    <hr>
    <RouterLink :to="{name: 'DetailView', params: {id:article.id}}">
      [DETAIL]
    </RouterLink>
  </div>
</template>

<script setup>
  import { RouterLink } from 'vue-router';
  defineProps({
    article: Object
  })

</script>

<style scoped>

</style>