import { createRouter, createWebHistory } from 'vue-router'
import { useStore } from '../store/index'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: () => import('../components/LoginRoom.vue')
  },
  {
    path: '/eval',
    name: 'Eval', 
    component: () => import('../components/EvalRoom.vue'),
  },
  {
    path: '/gen',
    name: 'Gen', 
    component: () => import('../components/GenRoom.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(process.env.NODE_ENV == 'production' ? '/racetrack/': './'),
  routes: routes
})

router.beforeEach((to) => {
  const store = useStore()
  if (to.name !== 'Login' && !store.hasLogin) {
    return { name: 'Login' }
  }
})

export default router