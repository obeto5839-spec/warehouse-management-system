<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="layout-aside">
      <div class="logo-area">
        <el-icon :size="24" color="#409EFF"><Box /></el-icon>
        <span v-show="!sidebarCollapsed" class="logo-text">仓库管理系统</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        :collapse="sidebarCollapsed"
        router
        background-color="#001529"
        text-color="#ffffffb3"
        active-text-color="#409EFF"
        class="sidebar-menu"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧内容 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon
            class="collapse-btn"
            :size="20"
            @click="toggleSidebar"
          >
            <Fold v-if="!sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="success" size="small">运行中</el-tag>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/store'

const route = useRoute()
const appStore = useAppStore()

const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)
const toggleSidebar = () => appStore.toggleSidebar()

const currentRoute = computed(() => route.path)

const menuItems = [
  { path: '/dashboard', title: '首页概览', icon: 'DataBoard' },
  { path: '/receiving', title: '收货录入', icon: 'DocumentAdd' },
  { path: '/sku', title: 'SKU 管理', icon: 'Cpu' },
  { path: '/items', title: '配件管理', icon: 'Ticket' },
  { path: '/machine', title: '整机管理', icon: 'Monitor' },
  { path: '/locations', title: '库位管理', icon: 'OfficeBuilding' },
  { path: '/inventory', title: '库存操作', icon: 'Box' },
  { path: '/outbound', title: '出库管理', icon: 'Van' },
]

const currentTitle = computed(() => {
  const item = menuItems.find((m) => m.path === route.path)
  return item ? item.title : ''
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-aside {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
}

.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid #ffffff1a;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

.layout-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 1;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  cursor: pointer;
  color: #333;
}

.collapse-btn:hover {
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.layout-main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
