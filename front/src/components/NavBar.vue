<script setup>
import { computed } from 'vue'
import { mdiClose } from '@mdi/js'
import { containerMaxW } from '@/config.js'
import BaseIcon from '@/components/BaseIcon.vue'
import NavBarMenuList from '@/components/NavBarMenuList.vue'
import NavBarItemPlain from '@/components/NavBarItemPlain.vue'
import TopLeftLinks from '@/components/TopLeftLinks.vue'

const props = defineProps({
  menu: {
    type: Array,
    required: true,
  },
  asideMenu: {
    type: Array,
    default: null,
  },
})

const emit = defineEmits(['menu-click'])

const menuClick = (event, item) => {
  emit('menu-click', event, item)
}

const activeMenu = computed(() => (props.asideMenu ? props.asideMenu : props.menu))
</script>

<template>
  <nav
    class="fixed inset-x-0 top-0 z-30 h-14 w-screen bg-gray-50 transition-(--transition-position) lg:w-auto dark:bg-slate-800"
  >
    <div class="flex lg:items-stretch" :class="containerMaxW">
      <!-- main slot area (left) - top-left hover links + slot -->
      <div class="flex h-14 flex-1 items-center gap-3">
        <TopLeftLinks />
        <slot />
      </div>
      <div
        class="absolute top-14 left-0 max-h-[calc(100dvh-(--spacing(14)))] w-screen overflow-y-auto bg-gray-50 shadow-lg hidden lg:static lg:flex lg:w-auto lg:overflow-visible lg:shadow-none dark:bg-slate-800"
      >
        <div class="flex items-center px-3 py-2">
        </div>
        <NavBarMenuList :menu="activeMenu" @menu-click="menuClick" />
      </div>
    </div>
  </nav>
</template>
