<script setup>
import { computed } from 'vue'
import { useAccountStore } from '@/stores/accounts'
import { useDarkModeStore } from '@/stores/darkMode'

import NavBar from '@/components/NavBar.vue'
import buildMenuNavBar from '@/menuNavBar'

const accountStore = useAccountStore()
const darkModeStore = useDarkModeStore()
const isCuteTheme = computed(() => true)

const menuNavBar = computed(() => buildMenuNavBar(accountStore.isLogin))

const menuClick = (event, item) => {
  if (item.isToggleLightDark) {
    darkModeStore.set(null, true)
    return
  }

  if (item.isLogout) {
    accountStore.logOut()
    alert('로그아웃 완료')
  }
}
</script>

<template>
  <div
    class="min-h-screen dark:text-slate-100"
    :class="isCuteTheme ? 'cute-theme bg-sky-50 dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'"
  >
    <NavBar :menu="menuNavBar" @menu-click="menuClick" />
    <div class="pt-14">
      <slot />
    </div>
  </div>
</template>
