<script setup>
import { computed } from 'vue'
import { useMainStore } from '@/stores/main'
import { useAccountStore } from '@/stores/accounts'

const mainStore = useMainStore()
const accountStore = useAccountStore()

const avatarSrc = computed(() => {
  const DEFAULT_AVATAR = '/usericon.png'
  const API_BASE = 'http://127.0.0.1:8000'

  const val = mainStore.userAvatarUrl || accountStore.avatar

  if (!val || typeof val !== 'string' || !val.trim()) return DEFAULT_AVATAR
  if (val.startsWith('blob:') || val.startsWith('http')) return val
  if (val.startsWith('/')) return `${API_BASE}${val}?t=${Date.now()}`
  return DEFAULT_AVATAR
})
</script>

<template>
  <img
    :src="avatarSrc"
    class="w-32 h-32 rounded-full object-cover object-center border"
    style="width:128px;height:128px;"
  />
</template>
