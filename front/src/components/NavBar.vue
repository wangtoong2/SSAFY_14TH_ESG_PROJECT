<script setup>
import { computed } from 'vue'
import { containerMaxW } from '@/config.js'
import NavBarMenuList from '@/components/NavBarMenuList.vue'
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
    <div class="flex h-14 items-center" :class="containerMaxW">
      <!-- left: Home + optional slot -->
      <div class="flex h-14 flex-1 items-center gap-3 min-w-0">
        <TopLeftLinks />
        <slot />
      </div>
      <!-- right: always visible (dark mode + Menu) -->
      <div class="flex items-center px-3 flex-shrink-0 overflow-visible">
        <NavBarMenuList :menu="activeMenu" @menu-click="menuClick" />
      </div>
    </div>
  </nav>
</template>
