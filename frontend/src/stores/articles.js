import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'

export const useArticleStore = defineStore('article', () => {
  const articles = ref([])
  const API_URL = 'http://127.0.0.1:8000'
  const accountStore = useAccountStore()

  const getArticles = function() {
    axios({
      method : 'get',
      url: `${API_URL}/api/v1/articles/`,
      headers: {
        'Authorization': `Bearer ${accountStore.token}`
      }
    })
    .then(res => {
      console.log(res)
      articles.value = res.data
      // console.log(res.data)
    })
    .catch(err => console.log(err))
  }

  return { articles, API_URL, getArticles }
}, {persist: true})
