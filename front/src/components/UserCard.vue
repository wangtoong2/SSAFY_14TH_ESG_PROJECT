<script setup>
import { computed } from 'vue'
import { useMainStore } from '@/stores/main'
import BaseLevel from '@/components/BaseLevel.vue'
import UserAvatarCurrentUser from '@/components/UserAvatarCurrentUser.vue'
import CardBox from '@/components/CardBox.vue'

const mainStore = useMainStore()

const userName = computed(() => mainStore.userName)

const avatarSrc = computed(() => {
  if (mainStore.userAvatarUrl) {
    return `http://127.0.0.1:8000${mainStore.userAvatarUrl}?t=${Date.now()}`
  }
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${mainStore.userEmail || 'guest'}`
})

</script>

<template>
  <CardBox>
    <BaseLevel type="justify-around lg:justify-center">
      <UserAvatarCurrentUser class="lg:mx-12" />
      <div class="space-y-3 text-center md:text-left lg:mx-12">
        <h1 class="text-2xl">
          안녕하세요, <b>{{ userName }}</b>님!
        </h1>
        <!-- <p>Last login <b>12 mins ago</b> from <b>127.0.0.1</b></p> -->
      </div>
    </BaseLevel>
  </CardBox>
</template>
