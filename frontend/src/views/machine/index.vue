<template>
  <div class="page-container">
    <div class="page-header">
      <h2>整机管理</h2>
    </div>

    <!-- 查询整机 -->
    <el-card shadow="never">
      <div class="search-bar">
        <el-input
          v-model="querySn"
          placeholder="输入整机编码查询配件组成"
          style="width: 360px"
          clearable
          @keyup.enter="handleQuery"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleQuery">查询</el-button>
      </div>

      <!-- 整机信息 -->
      <div v-if="machineItems.length > 0" style="margin-top: 20px">
        <el-alert
          :title="`整机 ${querySn} 共 ${machineItems.length} 件配件，总成本 ¥${totalCost}`"
          type="info"
          show-icon
          :closable="false"
          style="margin-bottom: 16px"
        />
        <el-table :data="machineItems" stripe border>
          <el-table-column prop="item_sn" label="配件编码" />
          <el-table-column prop="sku_id" label="SKU ID" width="90" />
          <el-table-column prop="grade" label="成色" width="90">
            <template #default="{ row }">{{ row.grade || '-' }}</template>
          </el-table-column>
          <el-table-column prop="cost_price" label="成本价" width="110">
            <template #default="{ row }">¥{{ row.cost_price }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="location_id" label="库位" width="80">
            <template #default="{ row }">{{ row.location_id || '-' }}</template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getMachineItems } from '@/api/machine'
import { ElMessage } from 'element-plus'

const querySn = ref('')
const machineItems = ref([])

const totalCost = computed(() =>
  machineItems.value.reduce((sum, item) => sum + parseFloat(item.cost_price || 0), 0).toFixed(2)
)

const statusMap = {
  pending_shelving: '待上架',
  in_stock: '在库',
  sold: '已售',
  frozen: '冻结',
  maintenance: '维修中',
}
const statusTagMap = {
  pending_shelving: 'warning',
  in_stock: 'success',
  sold: 'info',
  frozen: 'danger',
  maintenance: '',
}
function statusText(s) { return statusMap[s] || s }
function statusTagType(s) { return statusTagMap[s] || '' }

async function handleQuery() {
  if (!querySn.value) {
    ElMessage.warning('请输入整机编码')
    return
  }
  try {
    const res = await getMachineItems(querySn.value)
    machineItems.value = res.data || []
  } catch {
    machineItems.value = []
  }
}
</script>
