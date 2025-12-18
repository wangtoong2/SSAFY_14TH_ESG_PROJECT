<template>
  <div>
    <h1>회원가입페이지 입니다.</h1>
    <!-- submitForm -->
      <form @submit.prevent="signUp">
        <div>
          <label for="username">아이디 : </label>
          <input type="text" id="username" v-model="username" >
        </div>
        <!-- <div>
          <label for="email">이메일 : </label>
          <input type="text" id="email" v-model="email" >
        </div> -->
        <div>
          <label for="password1">비밀번호 : </label>
          <input type="password" id="password1" v-model="password1" >
        </div>
        <div>
          <label for="password2">비밀번호 확인 : </label>
          <input type="password" id="password2" v-model="password2" >
        </div>
        <!-- <div>
          <label for="phonenumber">전화번호 : </label>
          <input type="text" id="phonenumber" v-model="phonenumber" >
        </div> -->
        <!-- 입력 방법 변경 - 년/월/일 -->
        <!-- <div>
          <label for="birth">생년월일 : </label>
          <input type="text" id="birth" v-model="birth" >
        </div> -->
        <!-- 남 / 여 선택형 -->
        <!-- <div>
          <label for="gender">성별 : </label>
          <input type="text" id="gender" v-model="gender" >
        </div> -->
        <!-- 토글 박스 선택형 -->
        <!-- <div>
          <label for="interest">관심분야 : </label>
          <input type="text" id="interest" v-model="interest" >
        </div> -->
        <button type="submit">회원가입</button>
      </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAccountStore } from '@/stores/accounts';

const accountStore = useAccountStore()

const username = ref(null)
// const email = ref(null)
const password1 = ref(null)
const password2= ref(null)
// const phonenumber= ref(null)
// const gender = ref(null)

const signUp = function(){
  const payload = {
    username : username.value,
    // email : email.value,
    password1 : password1.value,
    password2 : password2.value,
    // phonenumber : phonenumber.value,
    // gender : gender.value
  }
  console.log(payload)
  accountStore.signUp(payload)
}


</script>

<style scoped>

</style>