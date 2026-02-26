<template>
  <div class="page-container">
    <div class="page-header">
      <h2>出库管理</h2>
    </div>

    <el-row :gutter="20">
      <!-- 散件出库 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#F56C6C" :size="20"><Van /></el-icon>
              <span>散件出库</span>
            </div>
          </template>
          <el-form :model="shipForm" label-width="80px">
            <el-form-item label="订单号" required>
              <el-input v-model="shipForm.order_no" placeholder="输入订单号" />
            </el-form-item>
            <el-form-item label="配件编码" required>
              <el-input v-model="shipForm.item_sn" placeholder="扫描配件二维码" @blur="onItemSnBlur" />
            </el-form-item>
            <!-- 整机绑定提示 -->
            <el-alert
              v-if="bindingWarning"
              :title="bindingWarning"
              type="warning"
              show-icon
              :closable="false"
              style="margin-bottom: 12px"
            />
            <el-form-item label="售价" required>
              <el-input-number v-model="shipForm.sell_price" :precision="2" :min="0" :step="10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="买家信息">
              <el-input v-model="shipForm.buyer_info" placeholder="选填" />
            </el-form-item>
            <el-form-item>
              <el-button type="danger" :loading="shipLoading" @click="handleShip" style="width: 100%">
                确认出库
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 整机出库 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#409EFF" :size="20"><Monitor /></el-icon>
              <span>整机出库</span>
            </div>
          </template>
          <el-form :model="machineForm" label-width="80px">
            <el-form-item label="整机码" required>
              <el-input v-model="machineForm.machine_sn" placeholder="扫描整机二维码" @blur="onMachineSnBlur" />
            </el-form-item>
            <!-- 整机配件预览 -->
            <div v-if="machineItems.length > 0" class="machine-preview">
              <el-tag v-for="item in machineItems" :key="item.item_sn" style="margin: 2px 4px">
                {{ item.item_sn }}
              </el-tag>
              <div class="machine-cost">总成本：¥{{ machineTotalCost }}</div>
            </div>
            <el-form-item label="订单号" required>
              <el-input v-model="machineForm.order_no" placeholder="输入订单号" />
            </el-form-item>
            <el-form-item label="整机售价" required>
              <el-input-number v-model="machineForm.sell_price" :precision="2" :min="0" :step="100" style="width: 100%" />
            </el-form-item>
            <el-form-item label="买家信息">
              <el-input v-model="machineForm.buyer_info" placeholder="选填" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="machineLoading" @click="handleMachineShip" style="width: 100%">
                整机一键出库（{{ machineItems.length }} 件）
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 订单查询 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#67C23A" :size="20"><Search /></el-icon>
              <span>订单查询</span>
            </div>
          </template>
          <div class="search-bar" style="flex-direction: column; align-items: stretch">
            <el-input v-model="queryOrderNo" placeholder="输入订单号查询" clearable @keyup.enter="handleQueryOrder" />
            <el-button type="primary" @click="handleQueryOrder" style="margin-top: 8px">查询</el-button>
          </div>
          <el-descriptions
            v-for="record in orderDetail"
            :key="record.id"
            :column="1"
            border
            size="small"
            style="margin-top: 12px"
          >
            <el-descriptions-item label="配件">{{ record.item_sn }}</el-descriptions-item>
            <el-descriptions-item label="售价">¥{{ record.sell_price }}</el-descriptions-item>
            <el-descriptions-item label="买家">{{ record.buyer_info || '-' }}</el-descriptions-item>
            <el-descriptions-item label="时间">{{ record.outbound_time }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 出库记录列表 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>出库记录</span>
          <el-button type="primary" text @click="fetchList">刷新</el-button>
        </div>
      </template>
      <el-table :data="outboundList" v-loading="listLoading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="order_no" label="订单号" width="140" />
        <el-table-column prop="item_sn" label="配件编码" />
        <el-table-column prop="sell_price" label="售价" width="100">
          <template #default="{ row }">¥{{ row.sell_price }}</template>
        </el-table-column>
        <el-table-column prop="buyer_info" label="买家信息">
          <template #default="{ row }">{{ row.buyer_info || '-' }}</template>
        </el-table-column>
        <el-table-column prop="outbound_time" label="出库时间" width="170" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Van, Search, Monitor } from '@element-plus/icons-vue'
import { getOrderDetail, getOutboundList } from '@/api/outbound'
import { checkBinding, shipMachine, unbindAndSell } from '@/api/machine'
import { ElMessage, ElMessageBox } from 'element-plus'

const shipLoading = ref(false)
const machineLoading = ref(false)
const listLoading = ref(false)
const queryOrderNo = ref('')
const orderDetail = ref([])
const outboundList = ref([])
const bindingWarning = ref('')
const machineItems = ref([])

// 散件出库表单
const shipForm = ref({ order_no: '', item_sn: '', sell_price: 0, buyer_info: '' })

// 整机出库表单
const machineForm = ref({ machine_sn: '', order_no: '', sell_price: 0, buyer_info: '' })

const machineTotalCost = computed(() => {
  return machineItems.value.reduce((sum, item) => sum + parseFloat(item.cost_price || 0), 0).toFixed(2)
})

// 散件出库前检查是否属于整机
async function onItemSnBlur() {
  bindingWarning.value = ''
  if (!shipForm.value.item_sn) return
  try {
    const res = await checkBinding(shipForm.value.item_sn)
    const data = res.data
    if (data.is_bound) {
      bindingWarning.value = `该配件属于整机 ${data.machine_sn}（共 ${data.siblings.length} 件），将从整机中拆出单独出库`
    }
  } catch {
    // 忽略
  }
}

// 散件/拆件出库
async function handleShip() {
  const { order_no, item_sn, sell_price } = shipForm.value
  if (!order_no || !item_sn || !sell_price) {
    ElMessage.warning('请填写订单号、配件编码和售价')
    return
  }

  // 如果属于整机，二次确认
  if (bindingWarning.value) {
    try {
      await ElMessageBox.confirm(bindingWarning.value + '，确认继续？', '拆件提醒', {
        confirmButtonText: '确认拆出并出库',
        cancelButtonText: '取消',
        type: 'warning',
      })
    } catch {
      return
    }
  }

  shipLoading.value = true
  try {
    await unbindAndSell(shipForm.value)
    ElMessage.success('出库成功')
    shipForm.value = { order_no: '', item_sn: '', sell_price: 0, buyer_info: '' }
    bindingWarning.value = ''
    fetchList()
  } finally {
    shipLoading.value = false
  }
}

// 扫整机码 → 加载配件列表
async function onMachineSnBlur() {
  machineItems.value = []
  if (!machineForm.value.machine_sn) return
  try {
    const { getMachineItems } = await import('@/api/machine')
    const res = await getMachineItems(machineForm.value.machine_sn)
    machineItems.value = res.data || []
  } catch {
    machineItems.value = []
  }
}

// 整机一键出库
async function handleMachineShip() {
  const { machine_sn, order_no, sell_price } = machineForm.value
  if (!machine_sn || !order_no || !sell_price) {
    ElMessage.warning('请填写整机码、订单号和售价')
    return
  }
  if (machineItems.value.length === 0) {
    ElMessage.warning('整机下无可用配件')
    return
  }
  machineLoading.value = true
  try {
    const res = await shipMachine(machineForm.value)
    const data = res.data
    ElMessage.success(`整机出库成功！共 ${data.item_count} 件，利润 ¥${data.profit.toFixed(2)}`)
    machineForm.value = { machine_sn: '', order_no: '', sell_price: 0, buyer_info: '' }
    machineItems.value = []
    fetchList()
  } finally {
    machineLoading.value = false
  }
}

// 查询订单
async function handleQueryOrder() {
  if (!queryOrderNo.value) {
    ElMessage.warning('请输入订单号')
    return
  }
  try {
    const res = await getOrderDetail(queryOrderNo.value)
    orderDetail.value = res.data || []
    if (orderDetail.value.length === 0) ElMessage.info('未找到该订单')
  } catch {
    orderDetail.value = []
  }
}

// 加载出库列表
async function fetchList() {
  listLoading.value = true
  try {
    const res = await getOutboundList({ skip: 0, limit: 50 })
    outboundList.value = res.data || []
  } finally {
    listLoading.value = false
  }
}

onMounted(fetchList)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-weight: 600;
}

.machine-preview {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.machine-cost {
  margin-top: 8px;
  font-size: 13px;
  color: #E6A23C;
  font-weight: 600;
}

.field-hint {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}
</style>
