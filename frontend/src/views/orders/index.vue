<template>
  <div class="orders-page">
    <!-- 搜索筛选栏 -->
    <div class="filter-bar">
      <el-row :gutter="12" align="middle">
        <el-col :span="5">
          <el-input v-model="filters.customer_id" placeholder="搜索卖家ID/昵称" clearable prefix-icon="Search" @clear="fetchOrders" @keyup.enter="fetchOrders" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.platform" placeholder="回收渠道" clearable @change="fetchOrders" style="width:100%">
            <el-option label="淘宝" value="淘宝" />
            <el-option label="闲鱼" value="闲鱼" />
            <el-option label="微信" value="微信" />
            <el-option label="线下同城" value="线下同城" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.order_type" placeholder="物品大类" clearable @change="fetchOrders" style="width:100%">
            <el-option label="台式整机" value="台式整机" />
            <el-option label="笔记本" value="笔记本" />
            <el-option label="散件" value="散件" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.order_status" placeholder="订单状态" clearable @change="fetchOrders" style="width:100%">
            <el-option label="已打款，在途中" value="已打款，在途中" />
            <el-option label="未打款，在途中" value="未打款，在途中" />
            <el-option label="已打款，入库完毕" value="已打款，入库完毕" />
            <el-option label="验机不符，退货拦截" value="验机不符，退货拦截" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" icon="Search" @click="fetchOrders">查询</el-button>
          <el-button icon="Refresh" @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card" :class="{ 'stat-active': !filters.order_status }" @click="filterByStatus('')">
        <div class="stat-value">{{ stats.total || 0 }}</div>
        <div class="stat-label">全部订单</div>
      </div>
      <div class="stat-card paid-transit" :class="{ 'stat-active': filters.order_status === '已打款，在途中' }" @click="filterByStatus('已打款，在途中')">
        <div class="stat-value">{{ stats['已打款，在途中'] || 0 }}</div>
        <div class="stat-label">已打款，在途中</div>
      </div>
      <div class="stat-card unpaid-transit" :class="{ 'stat-active': filters.order_status === '未打款，在途中' }" @click="filterByStatus('未打款，在途中')">
        <div class="stat-value">{{ stats['未打款，在途中'] || 0 }}</div>
        <div class="stat-label">未打款，在途中</div>
      </div>
      <div class="stat-card completed" :class="{ 'stat-active': filters.order_status === '已打款，入库完毕' }" @click="filterByStatus('已打款，入库完毕')">
        <div class="stat-value">{{ stats['已打款，入库完毕'] || 0 }}</div>
        <div class="stat-label">已打款，入库完毕</div>
      </div>
      <div class="stat-card returned" :class="{ 'stat-active': filters.order_status === '验机不符，退货拦截' }" @click="filterByStatus('验机不符，退货拦截')">
        <div class="stat-value">{{ stats['验机不符，退货拦截'] || 0 }}</div>
        <div class="stat-label">验机不符，退货拦截</div>
      </div>
    </div>

    <!-- 订单表格 -->
    <div class="table-card">
      <el-table :data="orderList" v-loading="loading" stripe border style="width: 100%" 
        :header-cell-style="{ background: '#fafafa', fontWeight: 700 }"
        @row-click="showDetail">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="platform" label="渠道" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="platformTagType(row.platform)">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="customer_id" label="卖家ID" min-width="120" show-overflow-tooltip />
        <el-table-column prop="order_type" label="物品大类" width="100" align="center">
          <template #default="{ row }">
            <span>{{ typeIcon(row.order_type) }} {{ row.order_type }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.notes || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_amount" label="打款金额" width="110" align="right">
          <template #default="{ row }">
            <span class="price-text">¥{{ (row.payment_amount || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="order_status" label="状态" width="160" align="center">
          <template #default="{ row }">
            <el-select
              v-model="row.order_status"
              size="small"
              style="width: 140px"
              @change="(val) => handleStatusChange(row, val)"
              @click.stop
            >
              <el-option label="已打款，在途中" value="已打款，在途中" />
              <el-option label="未打款，在途中" value="未打款，在途中" />
              <el-option label="已打款，入库完毕" value="已打款，入库完毕" />
              <el-option label="验机不符，退货拦截" value="验机不符，退货拦截" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="showDetail(row)">详情</el-button>
            <el-button link type="danger" size="small" @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchOrders"
          @current-change="fetchOrders"
        />
      </div>
    </div>

    <!-- 订单详情抽屉 -->
    <el-drawer v-model="drawerVisible" :title="`订单详情 #${currentOrder.id || ''}`" size="520px" direction="rtl">
      <div v-if="currentOrder.id" class="detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4 class="section-title">📋 基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">回收渠道</span>
              <span class="detail-value">{{ currentOrder.platform }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">卖家ID</span>
              <span class="detail-value">{{ currentOrder.customer_id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">联系电话</span>
              <span class="detail-value">{{ currentOrder.phone || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">发货区域</span>
              <span class="detail-value">{{ currentOrder.region || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">物品大类</span>
              <span class="detail-value">{{ typeIcon(currentOrder.order_type) }} {{ currentOrder.order_type }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">订单状态</span>
              <el-tag :type="statusTagType(currentOrder.order_status)" effect="dark" size="small">{{ currentOrder.order_status }}</el-tag>
            </div>
          </div>
        </div>

        <!-- 配置详情 -->
        <div class="detail-section" v-if="parsedConfig">
          <h4 class="section-title">🖥️ 配置详情</h4>
          <!-- 台式整机清单 -->
          <template v-if="currentOrder.order_type === '台式整机' && parsedConfig.components">
            <div class="config-list">
              <div v-for="(comp, i) in parsedConfig.components" :key="i" class="config-line">
                <span class="config-label">{{ comp.label || comp.type }}</span>
                <span class="config-value">{{ comp.description || `${comp.brand || ''} ${comp.series || ''} ${comp.model || ''}`.trim() }}</span>
              </div>
              <template v-if="parsedConfig.extras && parsedConfig.extras.length > 0">
                <div class="config-divider"></div>
                <div v-for="(ext, i) in parsedConfig.extras" :key="'ext-'+i" class="config-line extra">
                  <span class="config-label">{{ ext.type }}</span>
                  <span class="config-value">{{ ext.description || `${ext.brand || ''} ${ext.model || ''}`.trim() }}</span>
                </div>
              </template>
            </div>
          </template>
          <!-- 笔记本 -->
          <template v-else-if="currentOrder.order_type === '笔记本'">
            <div class="config-list">
              <div class="config-line" v-if="parsedConfig.brand"><span class="config-label">品牌</span><span class="config-value">{{ parsedConfig.brand }}</span></div>
              <div class="config-line" v-if="parsedConfig.series"><span class="config-label">系列</span><span class="config-value">{{ parsedConfig.series }}</span></div>
              <div class="config-line" v-if="parsedConfig.cpu"><span class="config-label">CPU</span><span class="config-value">{{ parsedConfig.cpu }}</span></div>
              <div class="config-line" v-if="parsedConfig.gpu"><span class="config-label">显卡</span><span class="config-value">{{ parsedConfig.gpu }}</span></div>
              <div class="config-line" v-if="parsedConfig.ram"><span class="config-label">内存</span><span class="config-value">{{ parsedConfig.ram }}</span></div>
              <div class="config-line" v-if="parsedConfig.storage"><span class="config-label">存储</span><span class="config-value">{{ parsedConfig.storage }}</span></div>
              <div class="config-line" v-if="parsedConfig.screen"><span class="config-label">屏幕</span><span class="config-value">{{ parsedConfig.screen }}</span></div>
            </div>
          </template>
          <!-- 散件 -->
          <template v-else-if="currentOrder.order_type === '散件' && Array.isArray(parsedConfig)">
            <div class="config-list">
              <div v-for="(part, i) in parsedConfig" :key="i" class="config-line">
                <span class="config-label">{{ part.type }}</span>
                <span class="config-value">{{ part.brand }} {{ part.series || '' }} {{ part.model }}</span>
              </div>
            </div>
          </template>
          <!-- 原始JSON -->
          <template v-else>
            <pre class="config-raw">{{ currentOrder.config_detail }}</pre>
          </template>
        </div>

        <!-- 备注信息 -->
        <div class="detail-section">
          <h4 class="section-title">📝 备注信息</h4>
          <div class="detail-grid">
            <div class="detail-item" style="grid-column: 1 / -1">
              <span class="detail-label">备注</span>
              <span class="detail-value">{{ currentOrder.notes || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- 物流结算 -->
        <div class="detail-section">
          <h4 class="section-title">💰 物流结算</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">发货方式</span>
              <span class="detail-value">{{ currentOrder.shipping_method || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">打款金额</span>
              <span class="detail-value price-text">¥{{ (currentOrder.payment_amount || 0).toFixed(2) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">承担运费</span>
              <span class="detail-value">¥{{ (currentOrder.shipping_fee || 0).toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- 时间信息 -->
        <div class="detail-section">
          <h4 class="section-title">🕐 时间信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">创建时间</span>
              <span class="detail-value">{{ formatDate(currentOrder.created_at) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">更新时间</span>
              <span class="detail-value">{{ formatDate(currentOrder.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getOrders, getOrder, updateOrder, deleteOrder, getOrderStats } from '@/api/order'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const orderList = ref([])
const drawerVisible = ref(false)
const currentOrder = ref({})

const filters = reactive({
  customer_id: '',
  platform: '',
  order_type: '',
  order_status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const stats = reactive({
  total: 0,
  '已打款，在途中': 0,
  '未打款，在途中': 0,
  '已打款，入库完毕': 0,
  '验机不符，退货拦截': 0,
})

const parsedConfig = computed(() => {
  if (!currentOrder.value.config_detail) return null
  try {
    return JSON.parse(currentOrder.value.config_detail)
  } catch {
    return null
  }
})

function platformTagType(platform) {
  const map = { '闲鱼': 'warning', '淘宝': 'danger', '微信': 'success', '线下同城': 'info' }
  return map[platform] || ''
}

function typeIcon(type) {
  const map = { '台式整机': '🖥️', '笔记本': '💻', '散件': '🔧' }
  return map[type] || '📦'
}

function statusTagType(status) {
  const map = {
    '已打款，在途中': 'warning',
    '未打款，在途中': '',
    '已打款，入库完毕': 'success',
    '验机不符，退货拦截': 'danger',
  }
  return map[status] || 'info'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function filterByStatus(status) {
  filters.order_status = status
  pagination.page = 1
  fetchOrders()
}

async function fetchOrders() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    if (filters.customer_id) params.customer_id = filters.customer_id
    if (filters.platform) params.platform = filters.platform
    if (filters.order_type) params.order_type = filters.order_type
    if (filters.order_status) params.order_status = filters.order_status

    const res = await getOrders(params)
    if (res.data) {
      orderList.value = res.data.items || res.data || []
      pagination.total = res.data.total || orderList.value.length
    }
  } catch (e) {
    console.error('获取订单列表失败', e)
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const res = await getOrderStats()
    if (res.data) {
      // Reset stats
      stats['已打款，在途中'] = 0
      stats['未打款，在途中'] = 0
      stats['已打款，入库完毕'] = 0
      stats['验机不符，退货拦截'] = 0
      stats.total = 0
      // Fill from API response
      for (const [status, count] of Object.entries(res.data)) {
        if (stats.hasOwnProperty(status)) {
          stats[status] = count
        }
        stats.total += count
      }
    }
  } catch {
    // 统计接口可能不存在，忽略
  }
}

function resetFilters() {
  filters.customer_id = ''
  filters.platform = ''
  filters.order_type = ''
  filters.order_status = ''
  pagination.page = 1
  fetchOrders()
}

async function showDetail(row) {
  try {
    const res = await getOrder(row.id)
    currentOrder.value = res.data || row
  } catch {
    currentOrder.value = row
  }
  drawerVisible.value = true
}

async function handleStatusChange(row, newStatus) {
  try {
    await updateOrder(row.id, { order_status: newStatus })
    ElMessage.success(`订单 #${row.id} 状态已更新为「${newStatus}」`)
    fetchStats()
  } catch (e) {
    console.error('更新状态失败', e)
    ElMessage.error('状态更新失败')
    fetchOrders() // 回滚显示
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除订单 #${row.id} 吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
    })
    await deleteOrder(row.id)
    ElMessage.success('删除成功')
    fetchOrders()
    fetchStats()
  } catch {
    // 取消删除
  }
}

onMounted(() => {
  fetchOrders()
  fetchStats()
})
</script>

<style scoped>
.orders-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 筛选栏 */
.filter-bar {
  background: #fff;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

/* 统计卡片 */
.stats-row {
  display: flex;
  gap: 12px;
}
.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  text-align: center;
  border-top: 3px solid #409EFF;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.stat-card.stat-active { box-shadow: 0 0 0 2px #409EFF, 0 4px 12px rgba(0,0,0,0.1); }
.stat-card.paid-transit { border-top-color: #E6A23C; }
.stat-card.paid-transit.stat-active { box-shadow: 0 0 0 2px #E6A23C, 0 4px 12px rgba(0,0,0,0.1); }
.stat-card.unpaid-transit { border-top-color: #909399; }
.stat-card.unpaid-transit.stat-active { box-shadow: 0 0 0 2px #909399, 0 4px 12px rgba(0,0,0,0.1); }
.stat-card.completed { border-top-color: #67C23A; }
.stat-card.completed.stat-active { box-shadow: 0 0 0 2px #67C23A, 0 4px 12px rgba(0,0,0,0.1); }
.stat-card.returned { border-top-color: #F56C6C; }
.stat-card.returned.stat-active { box-shadow: 0 0 0 2px #F56C6C, 0 4px 12px rgba(0,0,0,0.1); }
.stat-value { font-size: 28px; font-weight: 700; color: #333; }
.stat-label { font-size: 12px; color: #999; margin-top: 4px; }

/* 表格卡片 */
.table-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.price-text { color: #F56C6C; font-weight: 600; }
.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 详情抽屉 */
.detail-content {
  padding: 0 4px;
}
.detail-section {
  margin-bottom: 24px;
}
.section-title {
  font-size: 15px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.detail-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}
.detail-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 配置清单 */
.config-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.config-line {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 8px 12px;
}
.config-line.extra {
  background: #fef9e7;
}
.config-label {
  width: 3.5rem;
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  color: #4B5563;
  flex-shrink: 0;
}
.config-value {
  flex: 1;
  font-size: 13px;
  color: #333;
  margin-left: 12px;
}
.config-divider {
  height: 1px;
  background: #e8e8e8;
  margin: 4px 0;
}
.config-raw {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  color: #666;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
