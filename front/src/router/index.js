import { createRouter, createWebHistory } from 'vue-router'
// import Style from '@/views/StyleView.vue'

import { useAccountStore } from '@/stores/accounts'


const routes = [
  {
    meta: {
      title: 'Dashboard',
    },
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
  },
  {
    meta: {
      title: 'Forms',
    },
    path: '/forms',
    name: 'forms',
    component: () => import('@/views/FormsView.vue'),
  },
  {
    meta: {
      title: 'Profile',
      requiresAuth: true,
    },
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfilePageView.vue'),
  },
  {
    meta: {
      title: 'Profile Edit',
      requiresAuth: true,
    },
    path: '/profile/edit',
    name: 'profile-edit',
    component: () => import('@/views/ProfileView.vue'),
  },
  {
    meta: {
      title: 'User Profile',
      requiresAuth: true,
    },
    path: '/users/:username',
    name: 'UserProfile',
    component: () => import('@/views/UserProfileView.vue'),
  },
  {
    meta: {
      title: 'Login',
    },
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  },
  // Legacy links exist on the login page; feature pages are not implemented.
  // Register redirects to avoid "No match found" console warnings.
  {
    meta: { title: 'Find Password' },
    path: '/find-password',
    redirect: { name: 'login' },
  },
  {
    meta: { title: 'Find ID' },
    path: '/find-id',
    redirect: { name: 'login' },
  },
  {
    meta: {
      title: 'Error',
    },
    path: '/error',
    name: 'error',
    component: () => import('@/views/ErrorView.vue'),
  },
  {
    meta: {
      title: 'Signup',
    },
    path: '/signup',
    name: 'Signup',
    component: () => import('@/views/SignUpView.vue'),
  },
  {
    meta: {
      title: 'Update',
    },
    path: '/update',
    name: 'Update',
    component: () => import('@/views/UpdateView.vue'),
  },
  {
    meta: {
      title: 'ArticleList',
      requiresAuth: true,
    },
    path: '/articlelist',
    name: 'ArticleList',
    component: () => import('@/views/ArticleListView.vue'),
  },
  {
    meta: {
      title: 'ArticleCreate',
      requiresAuth: true,
    },
    path: '/articles/create',
    name: 'ArticleCreate',
    component: () => import('@/views/CreateView.vue'),
  },
  {
    meta: {
      title: 'Recommend',
      requiresAuth: true,
    },
    path: '/recommend',
    name: 'RecommendView',
    component: () => import('@/views/RecommendView.vue'),
  },
  {
    meta: { title: 'Jobs' },
    path: '/jobs',
    name: 'JobsView',
    component: () => import('@/views/JobsView.vue'),
  },
  {
    meta: { title: 'My Favorites' },
    path: '/favorites',
    name: 'MyFavorites',
    component: () => import('@/views/MyFavoritesView.vue'),
  },
  {
    meta: { title: 'My Articles', requiresAuth: true },
    path: '/my/articles',
    name: 'MyArticles',
    component: () => import('@/views/MyArticlesView.vue'),
  },
  {
    meta: { title: 'My Comments', requiresAuth: true },
    path: '/my/comments',
    name: 'MyComments',
    component: () => import('@/views/MyCommentsView.vue'),
  },
  {
    meta: { title: 'Company Detail' },
    path: '/companies/:id',
    name: 'CompanyDetail',
    component: () => import('@/views/CompanyDetailView.vue'),
  },
  {
    meta: { title: 'Company Search' },
    path: '/company-search',
    name: 'CompanySearch',
    component: () => import('@/views/CompanySearchView.vue'),
  },
  {
    path: '/articles/:id',
    name: 'ArticleDetail',
    meta: { requiresAuth: true },
    component: () => import('@/views/ArticleDetailView.vue'),
  },
  {
    path: '/articles/:id/edit',
    name: 'ArticleEdit',
    meta: { requiresAuth: true },
    component: () => import('@/views/ArticleEditView.vue'),
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
})

router.beforeEach((to) => {
  const requiresAuth = to.matched.some((record) => record.meta?.requiresAuth)
  if (!requiresAuth) return true

  const accountStore = useAccountStore()
  if (accountStore?.isLogin) return true

  alert('로그인 후 이용해주세요')
  return { name: 'login', query: { redirect: to.fullPath } }
})

export default router
