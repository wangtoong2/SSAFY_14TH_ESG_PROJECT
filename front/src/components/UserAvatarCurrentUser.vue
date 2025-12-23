<script setup>
import { computed } from 'vue'
import { useMainStore } from '@/stores/main'
import { useAccountStore } from '@/stores/accounts'

const mainStore = useMainStore()
const accountStore = useAccountStore()

const avatarSrc = computed(() => {
  const val = mainStore.userAvatarUrl || accountStore.avatar
  console.log('🔥 resolved avatar value:', val)

  if (!val) {
    console.log('⚠️ fallback avatar')
    return `https://api.dicebear.com/7.x/avataaars/svg?seed=${mainStore.userEmail || 'guest'}`
  }

  if (val.startsWith('blob:') || val.startsWith('http')) {
    return val
  }

  return `http://127.0.0.1:8000${val}?t=${Date.now()}`
})
</script>

<template>
  <img
    :src="avatarSrc"
    class="w-32 h-32 rounded-full object-cover object-center border"
    style="width:128px;height:128px;"
  />
</template>
