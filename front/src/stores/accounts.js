// 

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useMainStore } from '@/stores/main'

export const useAccountStore = defineStore(
  'account',
  () => {
    const API_URL = 'http://127.0.0.1:8000'
    const token = ref(null)
    const userName = ref('')
    const router = useRouter()
    const avatar = ref(null)

    // restore persisted session on startup: if token persisted, set axios header and sync user
    if (token.value) {
      axios.defaults.headers.common.Authorization = `Token ${token.value}`
      axios
        .get(`${API_URL}/accounts/user/`)
        .then((userRes) => {
          const mainStore = useMainStore()
          mainStore.setUser({
            name: userRes.data.username,
            email: userRes.data.email,
            userPhonenumber: userRes.data.phone_number,
            userGender: userRes.data.gender,
            avatar: userRes.data.avatar,
          })

          userName.value = userRes.data.username
          avatar.value = userRes.data.avatar
        })
        .catch((err) => {
          console.error('Failed to restore user on startup', err.response?.data || err)
        })
    }

    /* ================= 회원가입 ================= */
    const signUp = async (payload) => {
      const { username, password1, password2 } = payload

      try {
        await axios.post(`${API_URL}/accounts/registration/`, {
          username,
          password1,
          password2,
        })

        // 회원가입 후 자동 로그인
        await logIn({ username, password: password1 })
      } catch (err) {
        console.error(err.response?.data || err)
      }
    }

    /* ================= 로그인 ================= */

  const logIn = async ({ username, password }) => {
    try {
      const res = await axios.post(`${API_URL}/accounts/login/`, {
        username,
        password,
      })

      token.value = res.data.key
      axios.defaults.headers.common.Authorization = `Token ${token.value}`

      const userRes = await axios.get(`${API_URL}/accounts/user/`)

      const mainStore = useMainStore()
      mainStore.setUser({
        name: userRes.data.username,
        email: userRes.data.email,
        avatar: userRes.data.avatar,
      })

      // persist these in this store so avatar & name survive logout/login cycles
      userName.value = userRes.data.username
      avatar.value = userRes.data.avatar

      router.push({ name: 'dashboard' })
    } catch (err) {
      console.error(err.response?.data || err)
    }
  }



    /* ================= 로그인 상태 ================= */
    const isLogin = computed(() => !!token.value)

    /* ================= 로그아웃 ================= */
    // const logOut = async () => {
    //   token.value = null
    //   userName.value = ''

    //   const mainStore = useMainStore()
    //   mainStore.setUser({ name: 'Guest', email: '' })

    //   delete axios.defaults.headers.common.Authorization
    //   localStorage.removeItem('account')

    //   router.push({ name: 'dashboard' })
    // }

    const logOut = () => {
      token.value = null
      userName.value = ''
      avatar.value = null

      delete axios.defaults.headers.common.Authorization
      // do not remove persisted store here; keep persisted token/user data handling to startup logic
      router.push({ name: 'dashboard' })
    }

    /* ================= 회원탈퇴 (프론트 전용) ================= */
    // stores/accounts.js
    const withdraw = async () => {
      const ok = confirm('정말 회원탈퇴 하시겠습니까?\n이 작업은 되돌릴 수 없습니다.')
      if (!ok) return

      try {
        await axios.delete(`${API_URL}/accounts/withdraw/`, {
          headers: {
            Authorization: `Token ${token.value}`,
          },
        })

        // 🔥 프론트 상태 정리
        token.value = null
        userName.value = ''

        delete axios.defaults.headers.common.Authorization
        localStorage.removeItem('account')

        alert('회원탈퇴가 완료되었습니다.')
        router.push({ name: 'login' })

      } catch (err) {
        console.error(err.response?.data || err)
        alert('회원탈퇴에 실패했습니다.')
      }
    }


    return {
      signUp,
      logIn,
      logOut,
      withdraw,
      token,
      userName,
      isLogin,
      avatar
    }
  },
  { persist: true }
)
