<script setup>
import { computed } from 'vue'
import { useAccountStore } from '@/stores/accounts'
// const props = defineProps({
//   username: {
//     type: String,
//     required: true,
//   },
//   avatar: String,
//   api: {
//     type: String,
//     default: 'avataaars',
//   },
// })

// const avatar = computed(
//   () =>
//     props.avatar ??
//     `https://api.dicebear.com/7.x/${props.api}/svg?seed=${props.username.replace(
//       /[^a-z0-9]+/gi,
//       '-',
//     )}.svg`,
// )

// const username = computed(() => props.username)

const accountStore = useAccountStore()

const userAvatar = computed(() => {
  return (
    accountStore.avatar ||
    `https://api.dicebear.com/7.x/avataaars/svg?seed=${accountStore.userName}`
  )
})

</script>

<template>
  <div>
    <img
      :src="avatar"
      :alt="username"
      class="block h-auto w-full max-w-full rounded-full bg-gray-100 dark:bg-slate-800"
    />
    <slot />
  </div>
</template>
