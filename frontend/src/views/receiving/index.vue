<template>
  <div class="page-container">
    <div class="page-header">
      <h2>收货录入</h2>
    </div>

    <!-- 第一步：选择收货类型 -->
    <el-card v-if="step === 'choose'" shadow="hover" class="choose-card">
      <div class="choose-title">请选择收货类型</div>
      <el-row :gutter="24" class="choose-row">
        <el-col :span="12">
          <div class="choose-item" @click="startMachine">
            <el-icon :size="48" color="#409EFF"><Monitor /></el-icon>
            <div class="choose-label">收整机</div>
            <div class="choose-desc">整机拆解录入，自动生成整机编码，配件关联绑定</div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="choose-item" @click="startPart">
            <el-icon :size="48" color="#67C23A"><Cpu /></el-icon>
            <div class="choose-label">收散件</div>
            <div class="choose-desc">单独配件录入，无整机绑定</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 第二步：整机录入 -->
    <div v-if="step === 'machine'">
      <!-- 整机信息条 -->
      <el-card shadow="never" class="machine-banner">
        <div class="banner-content">
          <div>
            <el-tag type="primary" size="large">整机模式</el-tag>
            <span class="machine-code">整机编码：{{ machineSn }}</span>
          </div>
          <el-button text type="danger" @click="resetAll">返回重选</el-button>
        </div>
      </el-card>

      <!-- 整机汇总 -->
      <el-card shadow="hover" style="margin-top: 12px" v-if="machineItemsList.length > 0">
        <template #header>
          <div class="summary-header">
            <span>已录入 {{ machineItemsList.length }} 件配件</span>
            <span class="summary-cost">总成本：¥{{ totalCost }}</span>
          </div>
        </template>
        <el-table :data="machineItemsList" stripe size="small">
          <el-table-column prop="item_sn" label="配件编码" />
          <el-table-column prop="sku_label" label="SKU" />
          <el-table-column prop="grade" label="成色" width="80">
            <template #default="{ row }">{{ row.grade || '-' }}</template>
          </el-table-column>
          <el-table-column prop="cost_price" label="成本价" width="100">
            <template #default="{ row }">¥{{ row.cost_price }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default><el-tag type="warning" size="small">待上架</el-tag></template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 录入表单 -->
      <el-card shadow="hover" style="margin-top: 12px">
        <template #header><span>录入配件</span></template>
        <el-form :model="form" label-width="90px">
          <el-form-item label="配件编码" required>
            <el-input v-model="form.item_sn" placeholder="扫码或手动输入唯一编码" ref="itemSnInput" />
          </el-form-item>
          <el-form-item label="关联SKU" required>
            <el-select
              v-model="form.sku_id"
              filterable remote reserve-keyword
              :remote-method="handleSkuSearch"
              :loading="skuLoading"
              placeholder="输入关键词搜索SKU"
              style="width: 100%"
              @change="onSkuSelected"
            >
              <el-option v-for="s in skuOptions" :key="s.id" :label="s.label" :value="s.id" />
            </el-select>
            <div v-if="selectedSkuLabel" class="field-hint ok">已选: {{ selectedSkuLabel }}</div>
          </el-form-item>
          <el-form-item label="成色">
            <el-input v-model="form.grade" placeholder="例如：99新、95新" />
          </el-form-item>
          <el-form-item label="原厂条码">
            <el-input v-model="form.factory_sn" placeholder="选填" />
          </el-form-item>
          <el-form-item label="成本价">
            <el-input-number v-model="form.cost_price" :precision="2" :min="0" :step="10" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="submitLoading" @click="handleSubmit" style="width: 100%">
              {{ step === 'machine' ? '录入并继续下一件' : '确认录入' }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 第二步：散件录入 -->
    <div v-if="step === 'part'">
      <el-card shadow="never" class="machine-banner">
        <div class="banner-content">
          <div>
            <el-tag type="success" size="large">散件模式</el-tag>
          </div>
          <el-button text type="danger" @click="resetAll">返回重选</el-button>
        </div>
      </el-card>

      <el-card shadow="hover" style="margin-top: 12px">
        <template #header><span>录入配件</span></template>
        <el-form :model="form" label-width="90px">
          <el-form-item label="配件编码" required>
            <el-input v-model="form.item_sn" placeholder="扫码或手动输入唯一编码" ref="itemSnInput" />
          </el-form-item>
          <el-form-item label="关联SKU" required>
            <el-select
              v-model="form.sku_id"
              filterable remote reserve-keyword
              :remote-method="handleSkuSearch"
              :loading="skuLoading"
              placeholder="输入关键词搜索SKU"
              style="width: 100%"
              @change="onSkuSelected"
            >
              <el-option v-for="s in skuOptions" :key="s.id" :label="s.label" :value="s.id" />
            </el-select>
            <div v-if="selectedSkuLabel" class="field-hint ok">已选: {{ selectedSkuLabel }}</div>
          </el-form-item>
          <el-form-item label="成色">
            <el-input v-model="form.grade" placeholder="例如：99新、95新" />
          </el-form-item>
          <el-form-item label="原厂条码">
            <el-input v-model="form.factory_sn" placeholder="选填" />
          </el-form-item>
          <el-form-item label="成本价">
            <el-input-number v-model="form.cost_price" :precision="2" :min="0" :step="10" />
          </el-form-item>
          <el-form-item>
            <el-button type="success" :loading="submitLoading" @click="handleSubmit" style="width: 100%">
              确认录入
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { Monitor, Cpu } from '@element-plus/icons-vue'
import { createItem } from '@/api/item'
import { autocompleteSku } from '@/api/sku'
import { ElMessage } from 'element-plus'

const step = ref('choose')
const machineSn = ref('')
const machineItemsList = ref([])
const submitLoading = ref(false)
const skuLoading = ref(false)
const skuOptions = ref([])
const selectedSkuLabel = ref('')
const itemSnInput = ref(null)

const form = ref({
  item_sn: '',
  sku_id: null,
  grade: '',
  factory_sn: '',
  cost_price: 0,
})

const totalCost = computed(() =>
  machineItemsList.value.reduce((sum, i) => sum + parseFloat(i.cost_price || 0), 0).toFixed(2)
)

function generateMachineSn() {
  const now = new Date()
  const dateStr = now.getFullYear().toString() +
    (now.getMonth() + 1).toString().padStart(2, '0') +
    now.getDate().toString().padStart(2, '0')
  const rand = Math.random().toString(36).substring(2, 6).toUpperCase()
  return `MAC-${dateStr}-${rand}`
}

function startMachine() {
  step.value = 'machine'
  machineSn.value = generateMachineSn()
}

function startPart() {
  step.value = 'part'
  machineSn.value = ''
}

function resetAll() {
  step.value = 'choose'
  machineSn.value = ''
  machineItemsList.value = []
  resetForm()
}

function resetForm() {
  form.value = { item_sn: '', sku_id: null, grade: '', factory_sn: '', cost_price: 0 }
  selectedSkuLabel.value = ''
  skuOptions.value = []
}

async function handleSkuSearch(keyword) {
  if (!keyword) { skuOptions.value = []; return }
  skuLoading.value = true
  try {
    const res = await autocompleteSku(keyword)
    skuOptions.value = res.data || []
  } finally {
    skuLoading.value = false
  }
}

function onSkuSelected(id) {
  const s = skuOptions.value.find(s => s.id === id)
  selectedSkuLabel.value = s ? s.label : ''
}

async function handleSubmit() {
  if (!form.value.item_sn || !form.value.sku_id) {
    ElMessage.warning('请填写配件编码并选择 SKU')
    return
  }

  const payload = {
    ...form.value,
    machine_sn: step.value === 'machine' ? machineSn.value : null,
  }

  submitLoading.value = true
  try {
    await createItem(payload)
    ElMessage.success('录入成功')

    if (step.value === 'machine') {
      machineItemsList.value.push({
        item_sn: form.value.item_sn,
        sku_label: selectedSkuLabel.value,
        grade: form.value.grade,
        cost_price: form.value.cost_price,
      })
    }

    resetForm()
    await nextTick()
    itemSnInput.value?.focus()
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.choose-card {
  border-radius: 8px;
  padding: 20px 0;
}

.choose-title {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 24px;
}

.choose-row {
  max-width: 700px;
  margin: 0 auto;
}

.choose-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 36px 20px;
  border: 2px solid #ebeef5;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s;
}

.choose-item:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.choose-label {
  font-size: 20px;
  font-weight: 600;
  margin-top: 16px;
  color: #303133;
}

.choose-desc {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
  text-align: center;
}

.machine-banner {
  border-radius: 8px;
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.machine-code {
  margin-left: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  font-family: monospace;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.summary-cost {
  color: #E6A23C;
  font-size: 16px;
}

.field-hint {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

.field-hint.ok {
  color: #67C23A;
}
</style>
