import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { reveal } from './motion'
import router from './router'
import { installAuth } from './services/http'
import { useAuthStore } from './stores/auth'
import './assets/styles/main.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// Connect the Axios interceptors to the auth store (see services/http.js).
const auth = useAuthStore(pinia)
installAuth({
  getToken: () => auth.accessToken,
  refresh: () => auth.refreshAccessToken(),
  onSessionExpired: () => {
    auth.clearSession()
    const current = router.currentRoute.value
    if (current.meta.requiresAuth) {
      router.replace({ name: 'login', query: { redirect: current.fullPath, expired: '1' } })
    }
  },
})

app.use(router)
app.directive('reveal', reveal)
app.mount('#app')
