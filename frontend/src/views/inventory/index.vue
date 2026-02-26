<template>
  <div class="page-container">
    <div class="page-header">
      <h2>库存操作</h2>
    </div>

    <el-row :gutter="20">
      <!-- 上架操作 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#67C23A" :size="20"><Top /></el-icon>
              <span>扫码上架</span>
            </div>
          </template>
          <el-form :model="shelveForm" label-width="90px">
            <el-form-item label="配件编码">
              <el-input v-model="shelveForm.item_sn" placeholder="扫描配件二维码" clearable />
            </el-form-item>
            <el-form-item label="库位编码">
              <el-input v-model="shelveForm.location_code" placeholder="扫描货架条码" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="success" :loading="shelveLoading" @click="handleShelve" style="width: 100%">
                确认上架
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 拣货操作 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon color="#E6A23C" :size="20"><Bottom /></el-icon>
              <span>扫码拣货</span>
            </div>
          </template>
          <el-form :model="pickForm" label-width="90px">
            <el-form-item label="配件编码">
              <el-input v-model="pickForm.item_sn" placeholder="扫描配件二维码" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" :loading="pickLoading" @click="handlePick" style="width: 100%">
                确认拣货
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 库位查询 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <el-icon color="#409EFF" :size="20"><Search /></el-icon>
          <span>库位查询</span>
        </div>
      </template>
      <div class="search-bar">
        <el-input
          v-model="queryCode"
          placeholder="输入库位编码查询物品"
          style="width: 300px"
          clearable
          @keyup.enter="handleLocationQuery"
        />
        <el-button type="primary" @click="handleLocationQuery">查询</el-button>
      </div>
      <el-table :data="locationItems" v-loading="queryLoading" stripe v-if="locationItems.length > 0">
        <el-table-column prop="item_sn" label="配件编码" />
        <el-table-column prop="sku_id" label="SKU ID" width="100" />
        <el-table-column prop="grade" label="成色" width="100" />
        <el-table-column prop="cost_price" label="成本价" width="120">
          <template #default="{ row }">¥{{ row.cost_price }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="success">{{ row.status === 'in_stock' ? '在库' : row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Top, Bottom, Search } from '@element-plus/icons-vue'
import { shelveItem, pickItem, getLocationItems } from '@/api/inventory'
import { ElMessage } from 'element-plus'

const shelveLoading = ref(false)
const pickLoading = ref(false)
const queryLoading = ref(false)

const shelveForm = ref({ item_sn: '', location_code: '' })
const pickForm = ref({ item_sn: '' })
const queryCode = ref('')
const locationItems = ref([])

async function handleShelve() {
  if (!shelveForm.value.item_sn || !shelveForm.value.location_code) {
    ElMessage.warning('请填写配件编码和库位编码')
    return
  }
  shelveLoading.value = true
  try {
    await shelveItem(shelveForm.value)
    ElMessage.success('上架成功')
    shelveForm.value = { item_sn: '', location_code: '' }
  } finally {
    shelveLoading.value = false
  }
}

async function handlePick() {
  if (!pickForm.value.item_sn) {
    ElMessage.warning('请填写配件编码')
    return
  }
  pickLoading.value = true
  try {
    await pickItem(pickForm.value)
    ElMessage.success('拣货成功')
    pickForm.value = { item_sn: '' }
  } finally {
    pickLoading.value = false
  }
}

async function handleLocationQuery() {
  if (!queryCode.value) {
    ElMessage.warning('请输入库位编码')
    return
  }
  queryLoading.value = true
  try {
    const res = await getLocationItems(queryCode.value)
    locationItems.value = res.data || []
    if (locationItems.value.length === 0) {
      ElMessage.info('该库位暂无物品')
    }
  } finally {
    queryLoading.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
</style>
