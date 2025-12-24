<script setup>
defineProps({
  noPadding: Boolean,
})
</script>

<template>
  <div class="flex-1 card-box-body" :class="{ 'p-6': !noPadding }">
    <slot />
  </div>
</template>
