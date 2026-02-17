import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from './layouts/PublicLayout.vue'
import AdminLayout from './layouts/AdminLayout.vue'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('./components/FrontPage.vue'),
      },
      {
        path: 'about',
        name: 'about',
        component: () => import('./views/AboutPage.vue'),
      },
    ],
  },
  {
    path: '/plague/login',
    name: 'admin-login',
    component: () => import('./components/LoginPage.vue'),
  },
  {
    path: '/plague',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'admin-articles',
        component: () => import('./views/AdminArticles.vue'),
      },
      {
        path: 'categories',
        name: 'admin-categories',
        component: () => import('./views/AdminCategories.vue'),
      },
      {
        path: 'media',
        name: 'admin-media',
        component: () => import('./views/AdminMedia.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = localStorage.getItem('token')
    if (!token) {
      next({ name: 'admin-login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
