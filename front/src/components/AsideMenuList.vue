<script setup>
import AsideMenuItem from '@/components/AsideMenuItem.vue'

defineProps({
  isDropdownList: Boolean,
  menu: {
    type: Array,
    required: true,
  },
  isCollapsed: Boolean,
})

const emit = defineEmits(['menu-click'])

const menuClick = (event, item) => {
  emit('menu-click', event, item)
}
</script>

<template>
  <ul>
    <AsideMenuItem
      v-for="(item, index) in menu"
      :key="index"
      :item="item"
      :is-dropdown-list="isDropdownList"
      :is-collapsed="isCollapsed"
      @menu-click="menuClick"
    />
  </ul>
</template>
