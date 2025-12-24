<template>
  <div class="relative group">
    <button class="px-3 py-2 text-sm font-medium rounded navbar-item-label hover:bg-gray-100 dark:hover:bg-slate-700">Links</button>

    <!-- invisible hover zone to make transition forgiving when moving cursor -->
    <div class="hover-zone"></div>

    <div
      class="pointer-events-none opacity-0 scale-95 transform transition-all duration-150 origin-top-left absolute left-0 top-full w-56 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 dark:bg-slate-800 group-hover:opacity-100 group-hover:scale-100 group-hover:pointer-events-auto z-50"
      style="margin-top:4px"
    >
      <ul class="py-2">
        <li>
          <RouterLink to="/" class="block px-4 py-2 text-sm text-slate-700 hover:bg-gray-50 dark:text-slate-200 dark:hover:bg-slate-700">홈으로</RouterLink>
        </li>
        <li>
          <RouterLink to="/jobs" class="block px-4 py-2 text-sm text-slate-700 hover:bg-gray-50 dark:text-slate-200 dark:hover:bg-slate-700">구인구직 사이트</RouterLink>
        </li>
        <li>
          <RouterLink to="/recommend" class="block px-4 py-2 text-sm text-slate-700 hover:bg-gray-50 dark:text-slate-200 dark:hover:bg-slate-700">추천 보기</RouterLink>
        </li>
        <li>
          <RouterLink to="/articlelist" class="block px-4 py-2 text-sm text-slate-700 hover:bg-gray-50 dark:text-slate-200 dark:hover:bg-slate-700">게시판</RouterLink>
        </li>
        <!-- external link removed per request -->
      </ul>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
/* keep minimal styling; Tailwind handles most */
.hover-zone {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% - 2px);
  height: 20px;
  pointer-events: auto; /* allow it to receive hover */
  background: transparent;
  z-index: 40;
}
</style>
