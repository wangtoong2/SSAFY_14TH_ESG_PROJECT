<script setup>
import { computed } from 'vue'
import { useDarkModeStore } from '@/stores/darkMode.js'
import { gradientBgPurplePink, gradientBgDark, gradientBgPinkRed } from '@/colors.js'

const props = defineProps({
  bg: {
    type: String,
    // Auth screens sometimes want a plain/soft background.
    // Making this optional avoids noisy console warnings when no gradient is desired.
    required: false,
    default: 'none',
    validator: (value) => ['none', 'purplePink', 'pinkRed'].includes(value),
  },
})

const colorClass = computed(() => {
  if (props.bg === 'none') {
    return ''
  }

  if (useDarkModeStore().isEnabled) {
    return gradientBgDark
  }

  switch (props.bg) {
    case 'purplePink':
      return gradientBgPurplePink
    case 'pinkRed':
      return gradientBgPinkRed
  }

  return ''
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center" :class="colorClass">
    <slot card-class="w-11/12 md:w-7/12 lg:w-6/12 xl:w-4/12 shadow-2xl" />
  </div>
</template>
