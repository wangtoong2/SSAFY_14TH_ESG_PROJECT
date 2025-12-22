<script setup>
import { reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAccountStore } from '@/stores/accounts'

import LayoutGuest from '@/layouts/LayoutGuest.vue'
import SectionFullScreen from '@/components/SectionFullScreen.vue'
import CardBox from '@/components/CardBox.vue'

const router = useRouter()
const accountStore = useAccountStore()

// 1) 상태: form 하나로 통일
const form = reactive({
  username: '',
  password1: '',
  password2: '',
  name: '',
  birth: '', // YYYYMMDD
  gender: '', // 'M' | 'F' | ''
  email: '',
})

// 2) 유효성 검사 (프론트 1차 방어)
const errors = computed(() => {
  const e = {}

  if (!form.username.trim()) e.username = '아이디를 입력하세요.'
  if (!form.password1) e.password1 = '비밀번호를 입력하세요.'
  if (form.password1 && form.password1.length < 8) e.password1 = '비밀번호는 8자 이상 권장입니다.'
  if (!form.password2) e.password2 = '비밀번호 확인을 입력하세요.'
  if (form.password1 && form.password2 && form.password1 !== form.password2)
    e.password2 = '비밀번호가 일치하지 않습니다.'

  if (form.birth && !/^\d{8}$/.test(form.birth)) e.birth = '생년월일은 8자리(YYYYMMDD)로 입력하세요.'
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = '이메일 형식이 올바르지 않습니다.'

  return e
})

const hasErrors = computed(() => Object.keys(errors.value).length > 0)

// 3) 성별 선택 핸들러
const setGender = (g) => {
  form.gender = g
}

// 4) submit (payload 매핑)
// - 지금은 네 accountStore.signUp이 username/password1/password2만 받는 구조라 거기에 맞춰 보냄.
// - name/birth/gender/email은 백엔드가 받는 API가 생기면 그때 확장하면 됨.
const signUp = async () => {
  // 프론트 유효성 검사
  if (hasErrors.value) {
    alert(Object.values(errors.value)[0]) // 첫 에러만 간단히
    return
  }

  try {
    await accountStore.signUp({
      username: form.username.trim(),
      password1: form.password1,
      password2: form.password2,
      // 확장 필드(백엔드에서 받을 때 사용):
      // name: form.name.trim(),
      // birth: form.birth,
      // gender: form.gender,
      // email: form.email.trim(),
    })

    // 5) 성공 후 이동
    // accountStore.signUp 내부에서 자동 로그인 + 라우팅을 이미 하고 있다면 여기 이동은 중복될 수 있음.
    // 일단 안전하게 로그인 페이지로 보내고 싶으면 아래처럼:
    // router.push({ name: 'login' })

  } catch (err) {
    console.error('회원가입 실패:', err)
    alert('회원가입에 실패했습니다.')
  }
}
</script>

<template>
  <LayoutGuest>
    <SectionFullScreen class="login-bg-soft">
      <CardBox class="login-card">
        <h1 class="signup-title">회원가입</h1>

        <!-- 폼은 하나만 -->
        <form @submit.prevent="signUp" class="space-y-5">
          <!-- 아이디 -->
          <div>
            <label for="username" class="block mb-2 font-semibold">아이디</label>
            <input
              id="username"
              type="text"
              v-model.trim="form.username"
              autocomplete="username"
              class="w-full px-3 py-2 border rounded"
            />
            <p v-if="errors.username" class="mt-1 text-sm text-red-500">{{ errors.username }}</p>
          </div>

          <!-- 비밀번호 -->
          <div>
            <label for="password1" class="block mb-2 font-semibold">비밀번호</label>
            <input
              id="password1"
              type="password"
              v-model="form.password1"
              autocomplete="new-password"
              class="w-full px-3 py-2 border rounded"
            />
            <p v-if="errors.password1" class="mt-1 text-sm text-red-500">{{ errors.password1 }}</p>
          </div>

          <!-- 비밀번호 확인 -->
          <div>
            <label for="password2" class="block mb-2 font-semibold">비밀번호 확인</label>
            <input
              id="password2"
              type="password"
              v-model="form.password2"
              autocomplete="new-password"
              class="w-full px-3 py-2 border rounded"
            />
            <p v-if="errors.password2" class="mt-1 text-sm text-red-500">{{ errors.password2 }}</p>
          </div>

          <!-- 이름 (백엔드 준비 전이면 일단 프론트만) -->
          <div>
            <label class="block mb-2 font-semibold">이름</label>
            <input
              type="text"
              v-model.trim="form.name"
              autocomplete="name"
              class="w-full px-3 py-2 border rounded"
            />
          </div>

          <!-- 생년월일 -->
          <div>
            <label class="block mb-2 font-semibold">생년월일</label>
            <input
              type="text"
              v-model.trim="form.birth"
              maxlength="8"
              placeholder="YYYYMMDD"
              inputmode="numeric"
              class="w-full px-3 py-2 border rounded"
            />
            <p class="mt-1 text-sm text-gray-500">8자리 숫자로 입력해주세요 (YYYYMMDD)</p>
            <p v-if="errors.birth" class="mt-1 text-sm text-red-500">{{ errors.birth }}</p>
          </div>

          <!-- 성별 -->
          <div>
            <label class="block mb-2 font-semibold">성별</label>
            <div class="flex gap-2">
              <button
                type="button"
                @click="setGender('M')"
                :class="[
                  'px-4 py-2 border rounded',
                  form.gender === 'M' ? 'bg-slate-900 text-white' : ''
                ]"
              >
                남자
              </button>
              <button
                type="button"
                @click="setGender('F')"
                :class="[
                  'px-4 py-2 border rounded',
                  form.gender === 'F' ? 'bg-slate-900 text-white' : ''
                ]"
              >
                여자
              </button>
              <button
                type="button"
                @click="setGender('')"
                :class="[
                  'px-4 py-2 border rounded',
                  form.gender === '' ? 'bg-slate-900 text-white' : ''
                ]"
              >
                선택안함
              </button>
            </div>
          </div>

          <!-- 이메일 -->
          <div>
            <label class="block mb-2 font-semibold">이메일</label>
            <input
              type="email"
              v-model.trim="form.email"
              autocomplete="email"
              class="w-full px-3 py-2 border rounded"
            />
            <p v-if="errors.email" class="mt-1 text-sm text-red-500">{{ errors.email }}</p>
          </div>

          <!-- 제출 -->
          <button
            type="submit"
            class="w-full py-3 bg-green-600 text-white rounded font-semibold disabled:opacity-50"
            :disabled="hasErrors"
          >
            회원가입
          </button>
        </form>
      </CardBox>
    </SectionFullScreen>
  </LayoutGuest>
</template>

<style scoped>
.signup-title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
  color: #111;
}
</style>
