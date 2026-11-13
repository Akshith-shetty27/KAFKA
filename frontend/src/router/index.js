import { createRouter, createWebHistory } from 'vue-router'

// Views are lazy-loaded so each page ships as its own chunk.
const routes = [
  {
    // Until the landing page exists (Phase 3) the root shows system status.
    path: '/',
    redirect: { name: 'status' },
  },
  {
    path: '/status',
    name: 'status',
    component: () => import('@/views/SystemStatusView.vue'),
    meta: { title: 'System status' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: 'Not found' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition ?? { top: 0 }
  },
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · KAFKA` : 'KAFKA — Interview Preparation'
})

export default router
