<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6" v-for="card in statCards" :key="card.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-card-body">
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.title }}</div>
            </div>
            <el-icon :size="40" :color="card.color">
              <component :is="card.icon" />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card shadow="hover" class="quick-actions">
      <template #header>
        <span class="card-title">快捷操作</span>
      </template>
      <el-row :gutter="16">
        <el-col :span="6" v-for="action in quickActions" :key="action.title">
          <el-button
            :type="action.type"
            :icon="action.icon"
            size="large"
            class="action-btn"
            @click="$router.push(action.path)"
          >
            {{ action.title }}
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '@/api/dashboard'

const statCards = ref([
  { title: 'SKU 种类', value: '--', icon: 'Cpu', color: '#409EFF', key: 'sku_count' },
  { title: '在库配件', value: '--', icon: 'Ticket', color: '#67C23A', key: 'in_stock_count' },
  { title: '库位数量', value: '--', icon: 'OfficeBuilding', color: '#E6A23C', key: 'location_count' },
  { title: '今日出库', value: '--', icon: 'Van', color: '#F56C6C', key: 'today_outbound' },
])

const quickActions = [
  { title: '收货录入', type: 'primary', icon: 'DocumentAdd', path: '/receiving' },
  { title: '配件贴码', type: 'success', icon: 'Ticket', path: '/items' },
  { title: '扫码上架', type: 'warning', icon: 'Top', path: '/inventory' },
  { title: '扫码出库', type: 'danger', icon: 'Van', path: '/outbound' },
]

async function fetchStats() {
  try {
    const res = await getDashboardStats()
    const data = res.data
    statCards.value.forEach((card) => {
      card.value = data[card.key] ?? '--'
    })
  } catch {
    // 请求失败保持 '--'
  }
}

onMounted(fetchStats)
</script>

<style scoped>
.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
}

.stat-card-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.quick-actions {
  border-radius: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.action-btn {
  width: 100%;
  height: 60px;
  font-size: 16px;
}
</style>
