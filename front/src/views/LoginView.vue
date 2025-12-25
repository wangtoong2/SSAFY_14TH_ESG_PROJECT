<template>
  <LayoutGuest>
    <SectionFullScreen
    v-slot="{ cardClass }"
    class="login-bg-soft"
    >
  <CardBox
  :class="[cardClass, 'login-card']"
  >
  <div class="flex justify-center">
    <RouterLink :to="{ name: 'dashboard' }" class="inline-block">
      <img src="/jobffy_logo.png" alt="logo" class="auth-logo" />
    </RouterLink>
  </div>
  <h1 class="login-title">로그인</h1>
      <form @submit.prevent="logIn">
        <FormField label="아이디">
          <FormControl
          v-model="username"
          :icon="mdiAccount"
          name="login"
          autocomplete="username"
          />
        </FormField>

        <FormField label="비밀번호">
          <FormControl
          v-model="password"
          :icon="mdiAsterisk"
          type="password"
          autocomplete="password"
          />
        </FormField>

        <!-- 메인 로그인 버튼 -->
        <BaseButton
        type="submit"
        color="success"
        label="로그인"
        :icon="mdiAccount"
        class="login-main-btn"
        />
      </form>

      <div class="mt-5">
        <BaseButton
          type="button"
          color="info"
          label="Google로 로그인"
          class="login-main-btn"
          @click="loginWithGoogle"
        />
      </div>
        <!-- 하단 링크 -->
        <div class="login-links">
          <RouterLink to="/find-password">비밀번호 찾기</RouterLink>
          <span>|</span>
          <RouterLink to="/find-id">아이디 찾기</RouterLink>
          <span>|</span>
          <RouterLink to="/signup">회원가입</RouterLink>
        </div>
        <div class="text-center mt-3">
          <router-link :to="{ name: 'dashboard' }" class="text-sm text-slate-600 hover:underline">메인으로</router-link>
        </div>
      </CardBox>
    </SectionFullScreen>
  </LayoutGuest>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SectionFullScreen from '@/components/SectionFullScreen.vue'
import CardBox from '@/components/CardBox.vue'
import FormCheckRadio from '@/components/FormCheckRadio.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import LayoutGuest from '@/layouts/LayoutGuest.vue'
import { mdiAccount, mdiAsterisk } from '@mdi/js'
import { useAccountStore } from '@/stores/accounts';
import { ref } from 'vue'
const accountStore = useAccountStore()

const username = ref(null)
const password = ref(null)

const logIn = function () {
  const payload = {
    username : username.value,
    password : password.value,
  }
  accountStore.logIn(payload)
}

const router = useRouter()

function _parseHashParams() {
  const hash = window.location.hash || ''
  if (!hash.startsWith('#')) return {}
  const raw = hash.slice(1)
  const params = new URLSearchParams(raw)
  return Object.fromEntries(params.entries())
}

async function _handleGoogleCallbackFromHash() {
  const params = _parseHashParams()
  const accessToken = params.access_token
  if (!accessToken) return

  // remove token from URL to avoid re-processing on refresh
  window.history.replaceState({}, document.title, window.location.pathname + window.location.search)

  await accountStore.socialLogInGoogle({ accessToken })
}

function loginWithGoogle() {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  if (!clientId) {
    alert('VITE_GOOGLE_CLIENT_ID가 설정되지 않았습니다.\nfront/.env.local에 VITE_GOOGLE_CLIENT_ID를 추가한 뒤 npm run dev를 재시작하세요.')
    return
  }

  const redirectUri = `${window.location.origin}/login`
  const scope = encodeURIComponent('openid email profile')
  const state = Math.random().toString(36).slice(2)

  // Dev-friendly implicit flow (returns access_token in URL hash)
  const authUrl =
    'https://accounts.google.com/o/oauth2/v2/auth' +
    `?client_id=${encodeURIComponent(clientId)}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&response_type=token` +
    `&scope=${scope}` +
    `&include_granted_scopes=true` +
    `&prompt=select_account` +
    `&state=${encodeURIComponent(state)}`

  window.location.assign(authUrl)
}

onMounted(() => {
  _handleGoogleCallbackFromHash()
})

// const submit = () => {
//   router.push('/dashboard')
// }
</script>

<style scoped>
.login-bg {
  background-color: #f5f6f7;
}

.login-main-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
}

.login-links {
  margin-top: 16px;
  text-align: center;
  font-size: 13px;
  color: #666;
}

.login-links a {
  color: #666;
  text-decoration: none;
}

.login-links a:hover {
  text-decoration: underline;
}

.login-links span {
  margin: 0 6px;
  color: #ccc;
}

.login-title {
  text-align: center;
  font-size: 28px;      /* 핵심: 크기 */
  font-weight: 700;
  margin-bottom: 32px; /* 제목과 첫 입력칸 거리 */
  color: #111;
}

.auth-logo {
  display: block;
  width: 140px;
  height: auto;
  margin: 0 auto 12px auto;
}
</style>
