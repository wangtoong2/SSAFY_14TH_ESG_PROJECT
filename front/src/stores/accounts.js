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
        userName.value = username

        const mainStore = useMainStore()
        mainStore.setUser({
          name: username,
          email: `${username}@example.com`,
        })

        axios.defaults.headers.common.Authorization = `Token ${token.value}`

        router.push({ name: 'dashboard' })
      } catch (err) {
        console.error(err.response?.data || err)
      }
    }

    /* ================= 로그인 상태 ================= */
    const isLogin = computed(() => !!token.value)

    /* ================= 로그아웃 ================= */
    const logOut = async () => {
      token.value = null
      userName.value = ''

      const mainStore = useMainStore()
      mainStore.setUser({ name: 'Guest', email: '' })

      delete axios.defaults.headers.common.Authorization
      localStorage.removeItem('account')

      router.push({ name: 'dashboard' })
    }

    /* ================= 회원탈퇴 (프론트 전용) ================= */
    const withdraw = async () => {
      const ok = confirm(
        '정말 회원탈퇴 하시겠습니까?\n이 작업은 되돌릴 수 없습니다.'
      )
      if (!ok) return

      token.value = null
      userName.value = ''

      const mainStore = useMainStore()
      mainStore.setUser({ name: 'Guest', email: '' })

      delete axios.defaults.headers.common.Authorization
      localStorage.removeItem('account')

      alert('회원탈퇴가 완료되었습니다.')
      router.push({ name: 'login' })
    }

    return {
      signUp,
      logIn,
      logOut,
      withdraw,
      token,
      userName,
      isLogin,
    }
  },
  { persist: true }
)
