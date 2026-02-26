import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页概览', icon: 'DataBoard' },
      },
      {
        path: 'receiving',
        name: 'Receiving',
        component: () => import('@/views/receiving/index.vue'),
        meta: { title: '收货录入', icon: 'DocumentAdd' },
      },
      {
        path: 'sku',
        name: 'SkuList',
        component: () => import('@/views/sku/index.vue'),
        meta: { title: 'SKU 管理', icon: 'Cpu' },
      },
      {
        path: 'items',
        name: 'ItemList',
        component: () => import('@/views/items/index.vue'),
        meta: { title: '配件管理', icon: 'Ticket' },
      },
      {
        path: 'locations',
        name: 'LocationList',
        component: () => import('@/views/locations/index.vue'),
        meta: { title: '库位管理', icon: 'OfficeBuilding' },
      },
      {
        path: 'machine',
        name: 'Machine',
        component: () => import('@/views/machine/index.vue'),
        meta: { title: '整机管理', icon: 'Monitor' },
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/inventory/index.vue'),
        meta: { title: '库存操作', icon: 'Box' },
      },
      {
        path: 'outbound',
        name: 'Outbound',
        component: () => import('@/views/outbound/index.vue'),
        meta: { title: '出库管理', icon: 'Van' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
