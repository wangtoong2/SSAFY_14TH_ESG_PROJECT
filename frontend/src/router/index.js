import { createRouter, createWebHistory } from 'vue-router'
import ArticleView from '@/views/ArticleView.vue';
import LoginView from '@/views/LoginView.vue';
import SignUpView from '@/views/SignUpView.vue';
import MainView from '@/views/MainView.vue';
import DetailView from '@/views/DetailView.vue';
import CreateView from '@/views/CreateView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
      path: '/sigup',
      name: 'SignUpView',
      component: SignUpView,
    },
    {
      path: '/login',
      name: 'LoginView',
      component: LoginView,
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
  ],
})

export default router
