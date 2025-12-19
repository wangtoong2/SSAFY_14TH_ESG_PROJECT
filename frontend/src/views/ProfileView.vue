<template>
    <div>
        {{ username }} 님의 프로필
    </div>
</template>

<script setup>
import { ref } from 'vue'; 
import { useAccountStore } from '@/stores/accounts';
import { useRouter } from 'vue-router';
const router = useRouter()

const accountStore = useAccountStore()
const username = accountStore.userName

</script>

<style scoped>

</style>