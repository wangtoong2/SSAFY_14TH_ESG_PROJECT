<template>
  <div>
    <h1>게시글 작성</h1>
    <form @submit.prevent="createArticle">
      <label for="title">제목 : </label>
      <input type="text" id="title" v-model.trim="title">
      <label for="content">내용 : </label>
      <textarea type="text" id="content" v-model.trim="content"></textarea><br>
      <input type="submit">
    </form>
  </div>
</template>

<script setup>
  import { ref } from 'vue';
  import axios from 'axios';
  import { useArticleStore } from '@/stores/articles';
  import { useRouter } from 'vue-router';
  import { useAccountStore } from '@/stores/accounts';

  const title = ref(null)
  const content = ref(null)

  const store = useArticleStore()
  const accountStore = useAccountStore()
  const router = useRouter()

  const createArticle = function(){
    axios({
      method : 'post',
      url: `${store.API_URL}/api/v1/articles/`,
      data : {
        title : title.value,
        content : content.value
      },
      headers: {
        'Authorization': `Token ${accountStore.token}`
      },
    })
    .then(() => {
      router.push({name : 'ArticleView'})
    })
    .catch(err => console.log(err))

  }

</script>

<style scoped>

</style>