import { RouteConfig } from 'vue-router'

const routes: RouteConfig[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { name: 'home', path: '', component: () => import('pages/Index.vue') },
      { name: 'projects', path: 'projects/', component: () => import('pages/Projects.vue') }
    ]
  },
  /*
  {
    path: '/map',
    component: () => import('layouts/MapLayout.vue'),
    children: [
      {path: '', component: () => import('pages/Map.vue')}
    ]
  },
  */
  {
    path: '/project/:id',
    component: () => import('layouts/ProjectLayout.vue'),
    children: [
      { path: 'dashboard/', component: () => import('pages/project/Dashboard.vue') },
      { path: 'level/:level_id', component: () => import('pages/project/Map.vue') },
      { path: 'tools/add-level', component: () => import('pages/project/tools/AddLevel.vue') },
      { path: 'level/:level_id/loadout-manager', component: () => import('pages/project/tools/LoadoutManager.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '*',
    component: () => import('pages/Error404.vue')
  }
]

export default routes
