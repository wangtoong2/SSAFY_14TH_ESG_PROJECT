import { defineStore } from "pinia";

export const useArticleStore = defineStore('article', () => {
  const articles = ref([])
  const API_URL = 'http://127.0.0.1:8000'

  const getArticles = function () {
    axios({
      method: 'get',
      url: `${API_URL}/api/v1/articles/`
    })
    .then(res => {
      articles.value = res.data
    })
    // DEBUG: 게시글 목록 로드 실패 확인용 로그
    .catch(err => console.error(err))
  }
  return {articles, API_URL, getArticles}
}, {persist: true})
