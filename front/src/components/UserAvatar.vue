<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: { type: String, default: null },      // explicit image URL/path/blob
  username: { type: String, default: '' },   // alt fallback
  size: { type: [Number, String], default: 40 }, // px
})

const resolvedSrc = computed(() => {
  const DEFAULT_AVATAR = '/usericon.png'
  const API_BASE = 'http://127.0.0.1:8000'

  const val = props.src
  if (!val || typeof val !== 'string' || !val.trim()) return DEFAULT_AVATAR
  if (val.startsWith('blob:') || val.startsWith('http')) return val
  if (val.startsWith('/')) return `${API_BASE}${val}?t=${Date.now()}`
  return DEFAULT_AVATAR
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
      :alt="props.username || 'avatar'"
      class="w-full h-full object-cover object-center"
    />
  </div>
</template>
