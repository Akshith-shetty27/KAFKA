import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

/*
 * Route meta:
 *   requiresAuth  – signed-in users only (redirects to /login?redirect=…)
 *   guestOnly     – signed-out users only (login/register)
 *   surface       – 'paper' | 'ink' | 'user' (user = the profile's theme)
 *   title         – document title
 * Child routes inherit their parent's meta.
 */
const routes = [
  {
    path: '/',
    component: () => import('@/components/layout/PublicLayout.vue'),
    meta: { surface: 'paper' },
    children: [{ path: '', name: 'landing', component: () => import('@/views/LandingView.vue') }],
  },
  {
    path: '/',
    component: () => import('@/components/layout/AuthLayout.vue'),
    meta: { guestOnly: true, surface: 'paper' },
    children: [
      { path: 'login', name: 'login', component: () => import('@/views/auth/LoginView.vue'), meta: { title: 'Sign in' } },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/views/auth/RegisterView.vue'),
        meta: { title: 'Create account' },
      },
    ],
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true, surface: 'user' },
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: 'Dashboard' },
      },
      {
        path: 'prepare',
        name: 'prepare',
        component: () => import('@/views/PrepareView.vue'),
        meta: { title: 'Prepare' },
      },
      { path: 'practice', redirect: { name: 'practice', params: { category: 'coding' } } },
      {
        path: 'practice/:category',
        name: 'practice',
        component: () => import('@/views/PracticeView.vue'),
        meta: { title: 'Practice' },
      },
      {
        path: 'questions/:slug',
        name: 'question',
        component: () => import('@/views/QuestionView.vue'),
        meta: { title: 'Question' },
      },
      {
        path: 'progress',
        name: 'progress',
        component: () => import('@/views/ProgressView.vue'),
        meta: { title: 'Progress' },
      },
      {
        path: 'ask/:id(\\d+)?',
        name: 'ask',
        component: () => import('@/views/AskKafkaView.vue'),
        meta: { title: 'Ask KAFKA' },
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/SettingsView.vue'),
        meta: { title: 'Settings' },
      },
    ],
  },
  {
    path: '/status',
    name: 'status',
    component: () => import('@/views/SystemStatusView.vue'),
    meta: { title: 'System status', surface: 'ink' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: 'Not found', surface: 'paper' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, top: 88 }
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.init() // restores the session once per page load

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  return true
})

/*
 * After a new deploy, an open tab may ask for an old page chunk that no longer
 * exists ("Failed to fetch dynamically imported module"). Reload once onto the
 * target URL to pick up the new build; the session flag prevents reload loops.
 */
router.onError((error, to) => {
  const chunkFailed = /dynamically imported module|Importing a module script failed|Loading chunk/i.test(error?.message ?? '')
  if (!chunkFailed) return
  try {
    if (sessionStorage.getItem('kafka:chunk-reload') === to.fullPath) return
    sessionStorage.setItem('kafka:chunk-reload', to.fullPath)
  } catch {
    /* storage unavailable: still try once */
  }
  window.location.assign(to.fullPath)
})

router.afterEach((to) => {
  try {
    sessionStorage.removeItem('kafka:chunk-reload')
  } catch {
    /* ignore */
  }
  document.title = to.meta.title ? `${to.meta.title} · KAFKA` : 'KAFKA — Interview Preparation'
})

export default router
