<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import SectionFullScreen from '@/components/SectionFullScreen.vue'
import CardBox from '@/components/CardBox.vue'
import FormCheckRadio from '@/components/FormCheckRadio.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import LayoutGuest from '@/layouts/LayoutGuest.vue'
import { mdiAccount, mdiAsterisk } from '@mdi/js'

const form = reactive({
  login: '',
  pass: '',
  remember: true,
})

const router = useRouter()

const submit = () => {
  router.push('/dashboard')
}
</script>

<template>
  <LayoutGuest>
    <SectionFullScreen
    v-slot="{ cardClass }"
  class="login-bg-soft"
  >
  <CardBox
    :class="[cardClass, 'login-card']"
    is-form
    @submit.prevent="submit"
  >
  <h1 class="login-title">로그인</h1>

        <FormField label="아이디">
          <FormControl
            v-model="form.login"
            :icon="mdiAccount"
            name="login"
            autocomplete="username"
          />
        </FormField>

        <FormField label="비밀번호">
          <FormControl
            v-model="form.pass"
            :icon="mdiAsterisk"
            type="password"
            autocomplete="current-password"
          />
        </FormField>

        <FormCheckRadio
          v-model="form.remember"
          label="로그인 상태 유지"
          :input-value="true"
        />

        <!-- 메인 로그인 버튼 -->
        <BaseButton
          type="submit"
          color="success"
          label="로그인"
          :icon="mdiAccount"
          class="login-main-btn"
        />

        <!-- 하단 링크 -->
        <div class="login-links">
          <RouterLink to="/find-password">비밀번호 찾기</RouterLink>
          <span>|</span>
          <RouterLink to="/find-id">아이디 찾기</RouterLink>
          <span>|</span>
          <RouterLink to="/signup">회원가입</RouterLink>
        </div>

      </CardBox>
    </SectionFullScreen>
  </LayoutGuest>
</template>

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
</style>
