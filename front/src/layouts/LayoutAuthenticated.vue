<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { mdiMenu } from '@mdi/js'
import { useAccountStore } from '@/stores/accounts'
import { useDarkModeStore } from '@/stores/darkMode'

import { menuAsideMainLogin, menuAsideMainLogout } from '@/menuAside'
import menuNavBar from '@/menuNavBar'

import BaseIcon from '@/components/BaseIcon.vue'
import NavBar from '@/components/NavBar.vue'
import NavBarItemPlain from '@/components/NavBarItemPlain.vue'
import FooterBar from '@/components/FooterBar.vue'

const accountStore = useAccountStore()
const darkModeStore = useDarkModeStore()
const router = useRouter()

const menuAsideMain = computed(() => (accountStore.isLogin ? menuAsideMainLogin : menuAsideMainLogout))

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
    :class="{
      'overflow-hidden lg:overflow-visible': isAsideMobileExpanded,
    }"
  >
    <div
      :class="[layoutAsidePadding, { 'ml-60 lg:ml-0': isAsideMobileExpanded }]"
      class="min-h-screen w-screen bg-gray-50 pt-14 transition-(--transition-position) lg:w-auto dark:bg-slate-800 dark:text-slate-100"
    >
      <NavBar :menu="menuNavBar" @menu-click="menuClick">
        <NavBarItemPlain use-margin>
          <!-- optional search slot -->
        </NavBarItemPlain>
      </NavBar>
      <slot />
      <FooterBar>
        <div class="flex items-center justify-center lg:justify-start">
        </div>
      </FooterBar>
    </div>
  </div>
</template>
