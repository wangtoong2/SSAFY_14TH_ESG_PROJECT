<script setup>
import { computed } from 'vue'
import { useAccountStore } from '@/stores/accounts'

const props = defineProps({
  src: { type: String, default: null },      // explicit image URL/path/blob
  username: { type: String, default: '' },   // alt fallback
  size: { type: [Number, String], default: 40 }, // px
})

const accountStore = useAccountStore()

const resolvedSrc = computed(() => {
  const val = props.src || accountStore.avatar || accountStore.userName
  if (!val) return `https://api.dicebear.com/7.x/avataaars/svg?seed=${(props.username || accountStore.userName || 'guest')}`
  if (val.startsWith('blob:') || val.startsWith('http')) return val
  // server-relative path
  return `http://127.0.0.1:8000${val}?t=${Date.now()}`
})

const sizePx = computed(() => {
  const n = typeof props.size === 'string' ? Number(props.size) : props.size
  return Number.isFinite(n) ? `${n}px` : '40px'
})
</script>

<template>
  <div :style="{ width: sizePx, height: sizePx }" class="inline-block overflow-hidden rounded-full bg-gray-100 dark:bg-slate-800">
    <img
      :src="resolvedSrc"
      :alt="props.username || accountStore.userName || 'avatar'"
      class="w-full h-full object-cover object-center"
    />
  </div>
</template>
