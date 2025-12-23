<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { mdiForwardburger, mdiBackburger, mdiMenu } from '@mdi/js'

import { useAccountStore } from '@/stores/accounts'
import { useDarkModeStore } from '@/stores/darkMode'

import { menuAsideMainLogin, menuAsideMainLogout } from '@/menuAside'
import menuNavBar from '@/menuNavBar'

import BaseIcon from '@/components/BaseIcon.vue'
import NavBar from '@/components/NavBar.vue'
import NavBarItemPlain from '@/components/NavBarItemPlain.vue'
import AsideMenu from '@/components/AsideMenu.vue'
import FooterBar from '@/components/FooterBar.vue'

const accountStore = useAccountStore()
const darkModeStore = useDarkModeStore()
const router = useRouter()

const menuAsideMain = computed(() => {
  return accountStore.isLogin
    ? menuAsideMainLogin
    : menuAsideMainLogout
})

const isAsideMobileExpanded = ref(false)
const isAsideLgActive = ref(false)
const layoutAsidePadding = 'xl:pl-60'

router.beforeEach(() => {
  isAsideMobileExpanded.value = false
  isAsideLgActive.value = false
})

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
      <NavBar
        :menu="menuNavBar"
        :class="[layoutAsidePadding, { 'ml-60 lg:ml-0': isAsideMobileExpanded }]"
        @menu-click="menuClick"
      >
        <NavBarItemPlain
          display="flex lg:hidden"
          @click.prevent="isAsideMobileExpanded = !isAsideMobileExpanded"
        >
          <BaseIcon :path="isAsideMobileExpanded ? mdiBackburger : mdiForwardburger" size="24" />
        </NavBarItemPlain>
        <NavBarItemPlain display="hidden lg:flex xl:hidden" @click.prevent="isAsideLgActive = true">
          <BaseIcon :path="mdiMenu" size="24" />
        </NavBarItemPlain>
        <NavBarItemPlain use-margin>
          <!-- <FormControl placeholder="Search (ctrl+k)" ctrl-k-focus transparent borderless /> -->
        </NavBarItemPlain>
      </NavBar>
      <AsideMenu
        :is-aside-mobile-expanded="isAsideMobileExpanded"
        :is-aside-lg-active="isAsideLgActive"
        :menu="menuAsideMain"
        :menu-bottom="menuAsideBottom"
        @menu-click="menuClick"
        @aside-lg-close-click="isAsideLgActive = false"
      />
      <slot />
      <FooterBar>
        <div class="flex items-center justify-center lg:justify-start">
        </div>
      </FooterBar>
    </div>
  </div>
</template>
