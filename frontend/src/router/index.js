import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NetworkDiagramView from "../views/NetworkDiagramView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeView
    },
    {
      path: '/stp',
      name: 'NetworkDiagram',
      component: NetworkDiagramView
    }
  ]
})

export default router
