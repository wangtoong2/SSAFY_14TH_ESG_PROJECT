<template>
  <div>
    <h1>메인페이지 입니다.</h1>
    <h2>{{isLoggedIn ? `${username}님 환영합니다.` : "로그인 해주세요"}}</h2>
    <br>
    <div>
      <form @submit.prevent="logOut">
        <input type="submit" value ="로그아웃" />
      </form>
      <form @submit.prevent="editProfile">
        <input type="submit" value ="정보수정" />
      </form>
      <form @submit.prevent="deleteAccounts">
        <input type="submit" value ="회원탈퇴"/>
      </form>
      <form @submit.prevent="profile">
        <input type="submit" value="프로필"/>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'; 
import { useAccountStore } from '@/stores/accounts';
import { useRouter } from 'vue-router';
const router = useRouter()

const accountStore = useAccountStore()
const username = accountStore.userName
const isLoggedIn = accountStore.isLogIn

// 로그아웃 함수
const logOut = () => {
  accountStore.logOut()
  // 로그아웃 후 홈페이지로 리다이렉션
  router.push({name : 'ArticleView'})
}

// 정보 수정 함수
const editProfile = () => {
  router.push({name: 'EditProfileView'})
}

// 회원 탈퇴 함수 (예시)
const deleteAccount = () => {
  // 회원 탈퇴 로직 (예 : API 호출)
  console.log("회원 탈퇴 실행")
  }

// 프로필 페이지 이동
const profile = () => {
  router.push({name: 'ProfileView'})
}

</script>

<style scoped>

</style>