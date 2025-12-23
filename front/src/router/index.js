import { createRouter, createWebHistory } from 'vue-router'
// import Style from '@/views/StyleView.vue'


const routes = [
  {
    meta: {
      title: 'Dashboard',
    },
    path: '/dashboard',
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
    },
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
  },
  {
    meta: {
      title: 'Login',
    },
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
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
      title: 'Create',
    },
    path: '/create',
    name: 'Create',
    component: () => import('@/views/CreateView.vue'),
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
    },
    path: '/articlelist',
    name: 'ArticleList',
    component: () => import('@/views/ArticleListView.vue'),
  },
  {
    path: '/articles/:id',
    name: 'ArticleDetail',
    component: () => import('@/views/ArticleDetailView.vue'),
  },
  {
    path: '/articles/:id/edit',
    name: 'ArticleEdit',
    component: () => import('@/views/ArticleEditView.vue'),
  }
  ,
  {
    meta: { title: '기업 추천' },
    path: '/recommend',
    name: 'recommend',
    component: () => import('@/views/RecommendView.vue'),
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
})

export default router
