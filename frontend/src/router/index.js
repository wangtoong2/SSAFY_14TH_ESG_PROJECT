import { createRouter, createWebHistory } from 'vue-router'
import { useAccountStore } from '@/stores/accounts';

import ArticleView from '@/views/ArticleView.vue';
import LogInView from '@/views/LoginView.vue';
import SignUpView from '@/views/SignUpView.vue';
import MainView from '@/views/MainView.vue';
import DetailView from '@/views/DetailView.vue';
import CreateView from '@/views/CreateView.vue';
import DeleteAccountView from '@/views/DeleteAccountView.vue';
import EditProfileView from '@/views/EditProfileView.vue';
import ProfileView from '@/views/ProfileView.vue';
import Style from '@/views/StyleView.vue';
import Home from '@/views/HomeView.vue';

const routes = [
  // 로그인 및 회원가입 관련 라우팅
  {
    path: '/login',
    name: 'LogInView',
    component: LogInView,
  },
  {
    path: '/signup',
    name: 'SignUpView',
    component: SignUpView,
  },
  {
    path: '/main',
    name: 'MainView',
    component: MainView,
  },
  {
    path: '/article',
    name: 'ArticleView',
    component: ArticleView,
  },
  {
    path: '/articles/:id',
    name: 'DetailView',
    component: DetailView,
  },
  {
    path: '/create',
    name: 'CreateView',
    component: CreateView,
  },
  {
    path: '/edit-profile',
    name: 'EditProfileView',
    component: EditProfileView,
  },
  {
    path: '/delete-account',
    name: 'DeleteAccountView',
    component: DeleteAccountView,
  },
  {
    path: '/profile',
    name: 'ProfileView',
    component: ProfileView,
  },

  // 대시보드 및 관리 페이지 관련 라우팅
  {
    meta: {
      title: 'Select style',
    },
    path: '/',
    name: 'style',
    component: Style,
  },
  {
    meta: {
      title: 'Dashboard',
    },
    path: '/dashboard',
    name: 'dashboard',
    component: Home,
  },
  {
    meta: {
      title: 'Tables',
    },
    path: '/tables',
    name: 'tables',
    component: () => import('@/views/TablesView.vue'),
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
      title: 'Ui',
    },
    path: '/ui',
    name: 'ui',
    component: () => import('@/views/UiView.vue'),
  },
  {
    meta: {
      title: 'Responsive layout',
    },
    path: '/responsive',
    name: 'responsive',
    component: () => import('@/views/ResponsiveView.vue'),
  },
  {
    meta: {
      title: 'Login',
    },
    path: '/login',
    name: 'login',
    component: () => import('@/views/LogInView.vue'),
  },
  {
    meta: {
      title: 'Error',
    },
    path: '/error',
    name: 'error',
    component: () => import('@/views/ErrorView.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 };
  },
});

// Navigation Guard for Login/Signup flows
router.beforeEach((to, from) => {
  const accountStore = useAccountStore();

  // If user is not logged in and trying to access ArticleView, redirect to login
  if (to.name === 'ArticleView' && !accountStore.isLogIn) {
    window.alert('로그인이 필요합니다.');
    console.log('로그아웃 완료');
    return { name: 'LogInView' };
  }

  // If user is logged in and trying to access LogInView or SignUpView, redirect to ArticleView
  if ((to.name === 'SignUpView' || to.name === 'LogInView') && accountStore.isLogIn) {
    window.alert('이미 로그인 되어 있습니다.');
    return { name: 'ArticleView' };
  }
});

export default router;
