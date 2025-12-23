import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useMainStore = defineStore('main', () => {
  const userName = ref('Guest')
  const userEmail = ref('')

  // const userAvatar = computed(
  //   () =>
  //     `https://api.dicebear.com/7.x/avataaars/svg?seed=${userEmail.value.replace(
  //       /[^a-z0-9]+/gi,
  //       '-',
  //     )}`,
  // )

  
  const userAvatarUrl = ref(null)

  const isFieldFocusRegistered = ref(false)

  const clients = ref([])
  const history = ref([])

  function setUser(payload) {
    if (payload.name !== undefined) {
      userName.value = payload.name
    }
    if (payload.email !== undefined) {
      userEmail.value = payload.email
    }
    if (payload.avatar !== undefined) {
      userAvatarUrl.value = payload.avatar
      console.log('✅ mainStore avatar set:', payload.avatar)
    }
  }


function fetchSampleClients() {
  axios
    .get(`data-sources/clients.json?v=3`)
    .then((result) => {
      clients.value = Array.isArray(result?.data?.data)
        ? result.data.data
        : []
    })
    .catch((error) => {
      console.error(error)
      clients.value = []   // ⭐ 실패해도 배열 유지
    })
}


  function fetchSampleHistory() {
    axios
      .get(`data-sources/history.json`)
      .then((result) => {
        history.value = result?.data?.data
      })
      .catch((error) => {
        alert(error.message)
      })
  }

  return {
    userName,
    userEmail,
    // userAvatar,
    setUser,
    isFieldFocusRegistered,
    clients,
    history,
    setUser,
    fetchSampleClients,
    fetchSampleHistory,
  }
})
