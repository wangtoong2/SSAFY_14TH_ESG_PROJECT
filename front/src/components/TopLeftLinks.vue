<template>
  <RouterLink
    :to="{ name: 'dashboard' }"
    class="relative block cursor-pointer select-none items-center lg:flex navbar-item-label dark:text-white dark:hover:text-slate-400 py-2 px-3"
  >
    <div class="flex items-center">
      <BaseIcon :path="mdiHome" />
      <span class="px-2">Home</span>
    </div>
  </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { mdiHome } from '@mdi/js'
import BaseIcon from '@/components/BaseIcon.vue'
</script>
