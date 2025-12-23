<script setup>
import { computed } from 'vue'
import { useMainStore } from '@/stores/main'

const mainStore = useMainStore()

const avatarSrc = computed(() => {
  console.log('🔥 userAvatarUrl:', mainStore.userAvatarUrl)

  if (mainStore.userAvatarUrl) {
    const url = `http://127.0.0.1:8000${mainStore.userAvatarUrl}?t=${Date.now()}`
    console.log('✅ avatar src:', url)
    return url
  }

  console.log('⚠️ fallback avatar')
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${mainStore.userEmail || 'guest'}`
})


</script>

<template>
  <img
    :src="avatarSrc"
    class="w-20 h-20 rounded-full object-cover border"
  />
</template>
