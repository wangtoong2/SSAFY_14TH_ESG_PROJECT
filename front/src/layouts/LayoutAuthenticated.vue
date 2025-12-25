<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { mdiMenu } from '@mdi/js'
import { useAccountStore } from '@/stores/accounts'
import { useDarkModeStore } from '@/stores/darkMode'

import { menuAsideMainLogin, menuAsideMainLogout } from '@/menuAside'
import buildMenuNavBar from '@/menuNavBar'

import BaseIcon from '@/components/BaseIcon.vue'
import NavBar from '@/components/NavBar.vue'
import NavBarItemPlain from '@/components/NavBarItemPlain.vue'
import FooterBar from '@/components/FooterBar.vue'

const accountStore = useAccountStore()
const darkModeStore = useDarkModeStore()
const router = useRouter()
const isCuteTheme = computed(() => true)

const menuAsideMain = computed(() => (accountStore.isLogin ? menuAsideMainLogin : menuAsideMainLogout))
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
  <div>
    <div
      :class="[
        'min-h-screen w-screen pt-14 transition-(--transition-position) lg:w-auto dark:text-slate-100',
        isCuteTheme ? 'cute-theme bg-sky-50 dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800',
      ]"
    >
      <NavBar :menu="menuNavBar" @menu-click="menuClick">
        <NavBarItemPlain use-margin>
          
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
