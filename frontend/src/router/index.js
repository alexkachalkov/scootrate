import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '../views/AdminLayout.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AdminRiders from '../views/AdminRiders.vue'
import AdminEvents from '../views/AdminEvents.vue'
import AdminResults from '../views/AdminResults.vue'
import PublicLayout from '../views/PublicLayout.vue'
import HomeView from '../views/HomeView.vue'
import RatingView from '../views/RatingView.vue'
import RiderView from '../views/RiderView.vue'
import EventsView from '../views/EventsView.vue'
import EventDetailView from '../views/EventDetailView.vue'
import AboutView from '../views/AboutView.vue'
import RulesView from '../views/RulesView.vue'
import ContactView from '../views/ContactView.vue'
import { ensureUser } from '../stores/auth'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      { path: '', name: 'home', component: HomeView },
      { path: 'rating', name: 'rating', component: RatingView },
      { path: 'r/:id', name: 'rider', component: RiderView, props: true },
      { path: 'events', name: 'events', component: EventsView },
      { path: 'e/:id', name: 'event-detail', component: EventDetailView, props: true },
      { path: 'about', name: 'about', component: AboutView },
      { path: 'rules', name: 'rules', component: RulesView },
      { path: 'contact', name: 'contact', component: ContactView }
    ]
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: AdminLogin
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: { name: 'admin-riders' }
      },
      {
        path: 'riders',
        name: 'admin-riders',
        component: AdminRiders,
        meta: { requiresAuth: true }
      },
      {
        path: 'events',
        name: 'admin-events',
        component: AdminEvents,
        meta: { requiresAuth: true }
      },
      {
        path: 'results',
        name: 'admin-results',
        component: AdminResults,
        meta: { requiresAuth: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  if (!to.meta.requiresAuth) {
    return next()
  }
  const user = await ensureUser()
  if (user) {
    return next()
  }
  return next({ name: 'admin-login', query: { redirect: to.fullPath } })
})

export default router
