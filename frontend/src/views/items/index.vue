<template>
  <div class="page-container">
    <div class="page-header">
      <h2>配件管理</h2>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
        录入配件（贴码）
      </el-button>
    </div>

    <!-- 扫码查询 -->
    <div class="search-bar">
      <el-input
        v-model="querySn"
        placeholder="输入或扫描配件编码查询"
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

    <!-- 查询结果 -->
    <el-card v-if="itemDetail" shadow="never">
      <el-descriptions title="配件详情" :column="2" border>
        <el-descriptions-item label="配件编码">{{ itemDetail.item_sn }}</el-descriptions-item>
        <el-descriptions-item label="SKU">
          <span v-if="itemDetail.sku_label">{{ itemDetail.sku_label }}</span>
          <span v-else style="color: #909399">ID: {{ itemDetail.sku_id }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="成色">{{ itemDetail.grade || '-' }}</el-descriptions-item>
        <el-descriptions-item label="原厂条码">{{ itemDetail.factory_sn || '-' }}</el-descriptions-item>
        <el-descriptions-item label="成本价">¥{{ itemDetail.cost_price }}</el-descriptions-item>
        <el-descriptions-item label="存放库位">
          <span v-if="itemDetail.location_code">{{ itemDetail.location_code }}<span v-if="itemDetail.location_name"> ({{ itemDetail.location_name }})</span></span>
          <el-tag v-else type="info" size="small">未上架</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="整机编码">
          <template v-if="itemDetail.machine_sn">
            <el-tag type="primary">{{ itemDetail.machine_sn }}</el-tag>
            <span style="margin-left: 8px; color: #909399; font-size: 12px">
              (整机共 {{ itemDetail.machine_item_count }} 件配件)
            </span>
          </template>
          <span v-else style="color: #909399">散件</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTagType(itemDetail.status)">{{ statusText(itemDetail.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ itemDetail.created_at }}</el-descriptions-item>
      </el-descriptions>

      <!-- 整机关联配件列表 -->
      <div v-if="itemDetail.machine_siblings && itemDetail.machine_siblings.length > 0" style="margin-top: 16px">
        <h4 style="margin-bottom: 8px">同整机其他配件</h4>
        <el-table :data="itemDetail.machine_siblings" stripe size="small" style="width: 100%">
          <el-table-column prop="item_sn" label="配件编码" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 新增弹窗 -->
    <el-dialog v-model="showCreateDialog" title="录入配件" width="500px">
      <el-form :model="createForm" label-width="90px">
        <el-form-item label="配件编码" required>
          <el-input v-model="createForm.item_sn" placeholder="扫码或手动输入唯一编码" />
        </el-form-item>
        <el-form-item label="关联SKU" required>
          <el-select
            v-model="createForm.sku_id"
            filterable
            remote
            reserve-keyword
            :remote-method="handleSkuSearch"
            :loading="skuSearchLoading"
            placeholder="输入关键词搜索（如 3060、华硕）"
            style="width: 100%"
            value-key="id"
            @change="onSkuSelected"
          >
            <el-option
              v-for="item in skuOptions"
              :key="item.id"
              :label="item.label"
              :value="item.id"
            />
          </el-select>
          <div v-if="selectedSkuLabel" class="field-hint" style="color: #67C23A">已选: {{ selectedSkuLabel }}</div>
        </el-form-item>
        <el-form-item label="成色">
          <el-input v-model="createForm.grade" placeholder="例如：99新、95新" />
        </el-form-item>
        <el-form-item label="原厂条码">
          <el-input v-model="createForm.factory_sn" placeholder="选填" />
        </el-form-item>
        <el-form-item label="成本价">
          <el-input-number v-model="createForm.cost_price" :precision="2" :min="0" :step="10" />
        </el-form-item>
        <el-form-item label="整机编码">
          <el-input v-model="createForm.machine_sn" placeholder="选填，整机录入时填写同一编码">
            <template #append>
              <el-button @click="generateMachineSn" title="自动生成整机编码">生成</el-button>
            </template>
          </el-input>
          <div class="field-hint">同一台整机的配件填写相同的整机编码</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { createItem, getItemDetail } from '@/api/item'
import { autocompleteSku } from '@/api/sku'
import { ElMessage } from 'element-plus'

const submitLoading = ref(false)
const showCreateDialog = ref(false)
const querySn = ref('')
const itemDetail = ref(null)
const skuSearchLoading = ref(false)
const skuOptions = ref([])
const selectedSkuLabel = ref('')

const createForm = ref({
  item_sn: '',
  sku_id: null,
  grade: '',
  factory_sn: '',
  cost_price: 0,
  machine_sn: '',
})

async function handleSkuSearch(keyword) {
  if (!keyword || keyword.length < 1) {
    skuOptions.value = []
    return
  }
  skuSearchLoading.value = true
  try {
    const res = await autocompleteSku(keyword)
    skuOptions.value = res.data || []
  } finally {
    skuSearchLoading.value = false
  }
}

function onSkuSelected(id) {
  const selected = skuOptions.value.find(s => s.id === id)
  selectedSkuLabel.value = selected ? selected.label : ''
}

function generateMachineSn() {
  const now = new Date()
  const dateStr = now.getFullYear().toString() +
    (now.getMonth() + 1).toString().padStart(2, '0') +
    now.getDate().toString().padStart(2, '0')
  const rand = Math.random().toString(36).substring(2, 6).toUpperCase()
  createForm.value.machine_sn = `MAC-${dateStr}-${rand}`
}

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

function statusText(status) {
  return statusMap[status] || status
}

function statusTagType(status) {
  return statusTagMap[status] || ''
}

async function handleQuery() {
  if (!querySn.value) {
    ElMessage.warning('请输入配件编码')
    return
  }
  try {
    const res = await getItemDetail(querySn.value)
    itemDetail.value = res.data
  } catch {
    itemDetail.value = null
  }
}

async function handleCreate() {
  if (!createForm.value.item_sn || !createForm.value.sku_id) {
    ElMessage.warning('请填写编码和 SKU ID')
    return
  }
  submitLoading.value = true
  try {
    await createItem(createForm.value)
    ElMessage.success('录入成功')
    showCreateDialog.value = false
    createForm.value = { item_sn: '', sku_id: null, grade: '', factory_sn: '', cost_price: 0, machine_sn: createForm.value.machine_sn }
    selectedSkuLabel.value = ''
  } finally {
    submitLoading.value = false
  }
}
</script>
