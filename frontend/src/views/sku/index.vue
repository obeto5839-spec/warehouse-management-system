<template>
  <div class="page-container">
    <div class="page-header">
      <h2>SKU 管理</h2>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">
        录入标准件
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <div class="search-bar">
        <el-select
          v-model="searchForm.category"
          placeholder="选择分类"
          filterable
          clearable
          style="width: 180px"
          @change="onSearchCategoryChange"
        >
          <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select
          v-model="searchForm.brand"
          placeholder="选择品牌"
          filterable
          clearable
          :disabled="!searchForm.category"
          style="width: 180px"
          @change="handleSearch"
        >
          <el-option v-for="b in searchBrandOptions" :key="b" :label="b" :value="b" />
        </el-select>
        <el-input
          v-model="searchForm.keyword"
          placeholder="型号/系列关键词搜索"
          clearable
          style="width: 220px"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never" style="margin-top: 16px">
      <el-table :data="skuList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="category" label="分类" width="90" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="series" label="系列" width="120">
          <template #default="{ row }">
            <span v-if="row.series">{{ row.series }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="型号" width="160" />
        <el-table-column label="规格" min-width="240">
          <template #default="{ row }">
            <template v-if="row.properties && Object.keys(row.properties).length > 0">
              <el-tag
                v-for="(val, key) in row.properties"
                :key="key"
                size="small"
                class="prop-tag"
                effect="plain"
              >
                {{ getPropertyLabel(row.category, key) }}: {{ val }}
              </el-tag>
            </template>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="skuList.length === 0 && !loading" class="empty-tip">
        请选择分类后搜索，或点击右上角录入新的标准件
      </div>
    </el-card>

    <!-- 新增弹窗 -->
    <el-dialog v-model="showCreateDialog" title="录入标准配件" width="560px" @close="resetCreateForm">
      <el-form :model="createForm" label-width="90px" class="create-form">
        <!-- 分类 -->
        <el-form-item label="分类" required>
          <el-select
            v-model="createForm.category"
            placeholder="选择或输入分类"
            filterable
            allow-create
            default-first-option
            style="width: 100%"
            @change="onCreateCategoryChange"
          >
            <el-option v-for="c in allCategories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>

        <!-- 品牌 -->
        <el-form-item label="品牌" required>
          <el-select
            v-model="createForm.brand"
            placeholder="选择或输入品牌"
            filterable
            allow-create
            default-first-option
            :disabled="!createForm.category"
            style="width: 100%"
          >
            <el-option v-for="b in createBrandOptions" :key="b" :label="b" :value="b" />
          </el-select>
          <div v-if="!createForm.category" class="field-hint">请先选择分类</div>
        </el-form-item>

        <!-- 系列 -->
        <el-form-item label="系列">
          <el-input
            v-model="createForm.series"
            placeholder="如：雪豹、酷睿、ROG STRIX、凌霜（选填）"
            :disabled="!createForm.brand"
          />
          <div class="field-hint">品牌下的产品系列，没有可留空</div>
        </el-form-item>

        <!-- 型号 -->
        <el-form-item label="型号" required>
          <el-input
            v-model="createForm.model_name"
            placeholder="如：RTX 4060 Ti、i5-13490F、B760I GAMING"
            :disabled="!createForm.brand"
          />
          <div v-if="!createForm.brand" class="field-hint">请先选择品牌</div>
        </el-form-item>

        <!-- 动态规格参数区域 -->
        <el-divider v-if="currentPropertyFields.length > 0" content-position="left">
          规格参数（选填）
        </el-divider>

        <el-form-item
          v-for="field in currentPropertyFields"
          :key="field.key"
          :label="field.label"
          :required="field.required"
        >
          <!-- select 类型字段 -->
          <el-select
            v-if="field.type === 'select'"
            v-model="createForm.properties[field.key]"
            :placeholder="field.placeholder"
            filterable
            allow-create
            default-first-option
            style="width: 100%"
          >
            <el-option
              v-for="opt in (field.options || [])"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
          <!-- input 类型字段 -->
          <el-input
            v-else
            v-model="createForm.properties[field.key]"
            :placeholder="field.placeholder"
          />
        </el-form-item>

        <div v-if="createForm.category && currentPropertyFields.length === 0" class="field-hint" style="text-align: center; padding: 8px 0">
          该分类暂无预定义规格参数，可直接提交
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleCreate">确定录入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { createSku, searchSkus, getCategories, getBrands, getPropertySchema } from '@/api/sku'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const submitLoading = ref(false)
const showCreateDialog = ref(false)
const skuList = ref([])

const categoryOptions = ref([])
const searchBrandOptions = ref([])
const createBrandOptions = ref([])
const searchForm = ref({ category: '', brand: '', keyword: '' })

const createForm = ref({ category: '', brand: '', series: '', model_name: '', properties: {} })

// 全部分类的属性 schema 缓存（用于表格中 label 映射）
const allPropertySchema = ref({})
// 当前选中分类的动态字段
const currentPropertyFields = ref([])

// 合并后端已有分类 + schema 预定义分类，供下拉选择
const allCategories = ref([])

// ---- 初始化 ----
async function init() {
  const [catRes, schemaRes] = await Promise.all([
    getCategories(),
    getPropertySchema(),
  ])
  categoryOptions.value = catRes.data || []
  allPropertySchema.value = schemaRes.data || {}

  const schemaKeys = Object.keys(allPropertySchema.value)
  const merged = new Set([...categoryOptions.value, ...schemaKeys])
  allCategories.value = [...merged]
}

// 根据 category + key 获取中文 label（用于表格展示）
function getPropertyLabel(category, key) {
  const fields = allPropertySchema.value[category]
  if (!fields) return key
  const f = fields.find(f => f.key === key)
  return f ? f.label : key
}

// ---- 加载品牌 ----
async function fetchBrands(category, target) {
  if (!category) { target.value = []; return }
  try {
    const res = await getBrands(category)
    target.value = res.data || []
  } catch { target.value = [] }
}

// ---- 搜索栏分类变化 ----
function onSearchCategoryChange(val) {
  searchForm.value.brand = ''
  fetchBrands(val, searchBrandOptions)
  if (val) handleSearch()
}

// ---- 新增弹窗分类变化 → 加载品牌 + 动态字段 ----
function onCreateCategoryChange(val) {
  createForm.value.brand = ''
  createForm.value.series = ''
  createForm.value.model_name = ''
  createForm.value.properties = {}
  fetchBrands(val, createBrandOptions)

  const fields = allPropertySchema.value[val]
  currentPropertyFields.value = fields || []
}

// ---- 搜索 ----
async function handleSearch() {
  if (!searchForm.value.category) {
    ElMessage.warning('请先选择分类')
    return
  }
  loading.value = true
  try {
    const res = await searchSkus(searchForm.value)
    skuList.value = res.data || []
  } finally {
    loading.value = false
  }
}

// ---- 打开弹窗 ----
function openCreateDialog() {
  showCreateDialog.value = true
}

// ---- 重置表单 ----
function resetCreateForm() {
  createForm.value = { category: '', brand: '', series: '', model_name: '', properties: {} }
  createBrandOptions.value = []
  currentPropertyFields.value = []
}

// ---- 提交 ----
async function handleCreate() {
  const { category, brand, model_name } = createForm.value
  if (!category || !brand || !model_name) {
    ElMessage.warning('请完整填写分类、品牌和型号')
    return
  }

  // 检查必填规格参数
  for (const field of currentPropertyFields.value) {
    if (field.required && !createForm.value.properties[field.key]) {
      ElMessage.warning(`请填写规格参数：${field.label}`)
      return
    }
  }

  submitLoading.value = true
  try {
    await createSku(createForm.value)
    ElMessage.success('录入成功')
    showCreateDialog.value = false
    await init()
    if (searchForm.value.category === category) handleSearch()
  } finally {
    submitLoading.value = false
  }
}

onMounted(init)
</script>

<style scoped>
.search-card {
  border-radius: 8px;
}

.empty-tip {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  font-size: 14px;
}

.create-form .field-hint {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

.prop-tag {
  margin: 2px 4px 2px 0;
}

.text-muted {
  color: #c0c4cc;
}
</style>
