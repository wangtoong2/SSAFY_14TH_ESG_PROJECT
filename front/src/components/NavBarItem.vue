<script setup>
import { mdiChevronUp, mdiChevronDown } from '@mdi/js'
import { RouterLink } from 'vue-router'
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useMainStore } from '@/stores/main.js'
import BaseIcon from '@/components/BaseIcon.vue'
import UserAvatarCurrentUser from '@/components/UserAvatarCurrentUser.vue'
import NavBarMenuList from '@/components/NavBarMenuList.vue'
import BaseDivider from '@/components/BaseDivider.vue'
import { useDarkModeStore } from '@/stores/darkMode'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['menu-click'])

const is = computed(() => {
  if (props.item.href) {
    return 'a'
  }

  if (props.item.to) {
    return RouterLink
  }

  return 'div'
})

const componentClass = computed(() => {
  const base = [
    isDropdownActive.value
      ? `navbar-item-label-active dark:text-slate-400`
      : `navbar-item-label dark:text-white dark:hover:text-slate-400`,
    // use 1.5x horizontal padding for the right hamburger button
    props.item.menu
      ? 'lg:py-2 lg:px-3'
      : props.item.isRightHamburger
      ? 'py-2 px-[1.125rem]'
      : 'py-2 px-3',
  ]

  if (props.item.isDesktopNoLabel) {
    base.push('lg:w-16', 'lg:justify-center')
  }

  return base
})

const itemLabel = computed(() =>
  props.item.isCurrentUser ? useMainStore().userName : props.item.label,
)

const isDropdownActive = ref(false)

const menuClick = (event) => {
  emit('menu-click', event, props.item)

  if (props.item.menu) {
    isDropdownActive.value = !isDropdownActive.value
  }
}

const menuClickDropdown = (event, item) => {
  emit('menu-click', event, item)
}

const root = ref(null)

const forceClose = (event) => {
  if (root.value && !root.value.contains(event.target)) {
    isDropdownActive.value = false
  }
}

onMounted(() => {
  if (props.item.menu) {
    window.addEventListener('click', forceClose)
  }
})

onBeforeUnmount(() => {
  if (props.item.menu) {
    window.removeEventListener('click', forceClose)
  }
})

const darkModeStore = useDarkModeStore()
</script>

<template>
  <BaseDivider v-if="item.isDivider" nav-bar />
  <component
    :is="is"
    v-else
    ref="root"
    class="relative block cursor-pointer select-none items-center lg:flex"
    :class="componentClass"
    :to="item.to ?? null"
    :href="item.href ?? null"
    :target="item.target ?? null"
    @click="menuClick"
  >
    <div class="flex items-center">
      <UserAvatarCurrentUser v-if="item.isCurrentUser" class="mr-3 inline-flex h-6 w-6" />
      <BaseIcon
        v-if="item.icon"
        :path="item.icon"
        :class="{ 'transition-colors': !darkModeStore.isInProgress }"
      />
      <span
        class="px-2"
        :class="{
          'lg:hidden': item.isDesktopNoLabel && item.icon,
          'transition-colors': !darkModeStore.isInProgress,
        }"
        >{{ itemLabel }}</span
      >
      <BaseIcon
        v-if="item.menu"
        :path="isDropdownActive ? mdiChevronUp : mdiChevronDown"
        :class="{ 'transition-colors': !darkModeStore.isInProgress }"
        class="hidden lg:inline-flex"
      />
    </div>
    <div
      v-if="item.menu"
      class="absolute top-full z-20 mt-2 rounded-lg border bg-white text-sm shadow-lg dark:border-slate-700 dark:bg-slate-800"
      :class="[
        { hidden: !isDropdownActive },
        item.isRightHamburger ? 'right-0' : 'left-0',
        item.isRightHamburger ? 'lg:min-w-[150%]' : 'lg:min-w-full',
      ]"
    >
      <NavBarMenuList :menu="item.menu" @menu-click="menuClickDropdown" />
    </div>
  </component>
</template>
