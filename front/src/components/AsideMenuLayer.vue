<script setup>
import { mdiClose, mdiMenu } from '@mdi/js'
import AsideMenuList from '@/components/AsideMenuList.vue'
import BaseIcon from '@/components/BaseIcon.vue'

defineProps({
  menu: {
    type: Array,
    required: true,
  },
  menuBottom: Array,
  isCollapsed: Boolean,
})

const emit = defineEmits(['menu-click', 'aside-lg-close-click', 'aside-collapse-toggle'])

const menuClick = (event, item) => {
  emit('menu-click', event, item)
}

const asideLgCloseClick = (event) => {
  emit('aside-lg-close-click', event)
}

const toggleCollapse = (e) => {
  emit('aside-collapse-toggle', e)
}
</script>

<template>
  <aside
    id="aside"
    :class="['fixed top-0 z-40 flex h-screen overflow-hidden transition-(--transition-position) lg:py-2 lg:pl-2', isCollapsed ? 'w-20' : 'w-60']"
  >
    <div class="aside flex flex-1 flex-col overflow-hidden lg:rounded-2xl bg-white dark:bg-slate-900 text-blue-600 dark:text-slate-300">
      <div class="aside-brand flex h-14 flex-row items-center justify-between bg-white dark:bg-slate-900">
        <div class="flex-1 text-center lg:pl-6 lg:text-left xl:pl-0 xl:text-center">
          <!-- logo removed by request -->
        </div>
        <div class="flex items-center gap-2 pr-2">
          <button class="p-2" @click.prevent="toggleCollapse">
            <BaseIcon :path="mdiMenu" />
          </button>
          <button class="hidden p-3 lg:inline-block xl:hidden" @click.prevent="asideLgCloseClick">
            <BaseIcon :path="mdiClose" />
          </button>
        </div>
      </div>
      <div
        class="aside-scrollbar flex-1 overflow-x-hidden overflow-y-auto dark:scrollbar-styled-dark"
      >
        <AsideMenuList :menu="menu" :is-collapsed="isCollapsed" @menu-click="menuClick" />
        <div class="px-6 py-3">
        </div>
      </div>

      <AsideMenuList v-if="menuBottom" :menu="menuBottom" :is-collapsed="isCollapsed" @menu-click="menuClick" />
    </div>
  </aside>
</template>
