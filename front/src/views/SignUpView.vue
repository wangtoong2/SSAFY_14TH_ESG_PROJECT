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
  username: '',
  password: '',
  passwordConfirm: '',
  email: '',
  name: '',
  birth: '',
  gender: '',
  phone: '',
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
    <h1 class="signup-title" >회원가입</h1>

    <!-- 계정 정보 -->

    <FormField label="아이디">
        <FormControl
        v-model="form.login"
        :icon="mdiAccount"
        autocomplete="username"
        />
    </FormField>

    <FormField label="비밀번호">
        <FormControl
        v-model="form.pass"
        :icon="mdiAsterisk"
        type="password"
        autocomplete="new-password"
        />
    </FormField>

    <!-- 개인 정보 -->

    <FormField label="이름">
        <FormControl
        v-model="form.name"
        :icon="mdiAccount"
        autocomplete="name"
        />
    </FormField>

    <FormField
        label="생년월일"
        help="8자리 숫자로 입력해주세요 (YYYYMMDD)"
    >
        <FormControl
        v-model="form.birth"
        inputmode="numeric"
        maxlength="8"
        placeholder="19990101"
        />
    </FormField>

    <FormField label="성별">
        <div class="gender-group">
        <BaseButton outline label="남자" />
        <BaseButton outline label="여자" />
        <BaseButton outline label="선택안함" />
        </div>
    </FormField>

    <FormField label="이메일">
        <FormControl
        v-model="form.email"
        autocomplete="email"
        />
    </FormField>

    <!-- 제출 -->
    <BaseButton
        type="submit"
        color="success"
        label="회원가입"
        :icon="mdiAccount"
        class="login-main-btn"
    />
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

.gender-group {
  display: flex;
  gap: 8px;
}
.section-title {
  margin-top: 24px;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.gender-group {
  display: flex;
  gap: 8px;
}
.signup-title {
  text-align: center;
  font-size: 28px;      /* 핵심: 크기 */
  font-weight: 700;
  margin-bottom: 32px; /* 제목과 첫 입력칸 거리 */
  color: #111;
}



</style>
