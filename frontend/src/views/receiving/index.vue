<template>
  <div class="receiving-page">
    <div class="wizard-wrapper">
      <div class="wizard-card">
        <!-- 头部进度 -->
        <div class="wizard-header">
          <h2 class="wizard-title">{{ stepTitles[currentStep - 1] }}</h2>
          <div class="progress-bar">
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progressWidth }"></div>
            </div>
            <div class="progress-dots">
              <div v-for="(s, i) in stepLabels" :key="i"
                class="dot-item" :class="{ active: currentStep >= i + 1, current: currentStep === i + 1 }"
                @click="goToStep(i + 1)">
                <div class="dot-circle">{{ i + 1 }}</div>
                <span class="dot-text">{{ s }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 表单内容区 -->
        <div class="wizard-body">

          <!-- ====== Step 1: 卖家信息 ====== -->
          <div v-show="currentStep === 1" class="step-pane">
            <div class="field-block">
              <label class="field-title">1. 回收渠道</label>
              <div class="pill-group">
                <span v-for="p in platformOptions" :key="p.value"
                  class="pill" :class="{ selected: form.platform === p.value }"
                  @click="form.platform = p.value">{{ p.icon }} {{ p.label }}</span>
              </div>
            </div>
            <div class="field-block">
              <label class="field-title">2. 客户(卖家) ID / 昵称</label>
              <el-input v-model="form.customer_id" placeholder="输入闲鱼号或微信昵称" size="large" />
            </div>
            <div class="field-block">
              <label class="field-title">3. 卖家联系电话</label>
              <el-input v-model="form.phone" placeholder="输入手机号码" size="large" />
            </div>
            <div class="field-block">
              <label class="field-title">4. 发货区域</label>
              <el-input v-model="form.region" placeholder="如：广东省深圳市" size="large" />
            </div>
          </div>

          <!-- ====== Step 2: 配件明细 ====== -->
          <div v-show="currentStep === 2" class="step-pane">
            <!-- 物品大类选择 -->
            <div class="field-block">
              <label class="field-title">1. 物品大类</label>
              <div class="pill-group">
                <span v-for="t in typeOptions" :key="t.value"
                  class="pill" :class="{ selected: form.order_type === t.value }"
                  @click="onTypeChange(t.value)">{{ t.icon }} {{ t.label }}</span>
              </div>
            </div>

            <div class="divider"></div>

            <!-- ========== 台式整机：逐件子向导 ========== -->
            <template v-if="form.order_type === '台式整机'">
              <!-- 配件录入卡片 (非汇总状态) -->
              <div v-if="compStep <= COMPONENTS.length" class="comp-card">
                <div class="comp-header">
                  <div class="comp-progress">
                    <span class="comp-idx">{{ compStep }}/{{ COMPONENTS.length }}</span>
                    <span class="comp-name">{{ currentComp.icon }} {{ currentComp.label }}</span>
                  </div>
                  <el-button link type="info" @click="skipComponent">跳过 &rarr;</el-button>
                </div>
                <div class="comp-progress-bar">
                  <div class="comp-progress-fill" :style="{ width: `${(compStep / COMPONENTS.length) * 100}%` }"></div>
                </div>

                <!-- 品牌 -->
                <div class="spec-field">
                  <label class="spec-label">品牌</label>
                  <el-select
                    v-model="compData[compStep - 1].brand"
                    filterable allow-create default-first-option
                    placeholder="搜索或输入品牌"
                    style="width: 100%"
                    @change="onBrandChange"
                  >
                    <el-option v-for="b in brandOptions" :key="b" :label="b" :value="b" />
                  </el-select>
                </div>

                <!-- 系列（可选） -->
                <div class="spec-field">
                  <label class="spec-label">系列（选填）</label>
                  <el-input
                    v-model="compData[compStep - 1].series"
                    placeholder="如 ROG / TUF / 巨齿鲨（可留空）"
                    style="width: 100%"
                  />
                </div>

                <!-- 型号 -->
                <div class="spec-field">
                  <label class="spec-label">型号</label>
                  <el-select
                    v-model="compData[compStep - 1].model"
                    filterable allow-create default-first-option
                    :disabled="!compData[compStep - 1].brand"
                    placeholder="搜索或输入型号"
                    style="width: 100%"
                    :loading="modelLoading"
                    @change="onModelChange"
                  >
                    <el-option v-for="m in modelOptions" :key="m.model_name" :label="m.model_name" :value="m.model_name" />
                  </el-select>
                </div>

                <!-- 动态规格参数 -->
                <div v-if="currentSpecFields.length > 0" class="spec-dynamic">
                  <el-row :gutter="12">
                    <el-col :span="12" v-for="field in currentSpecFields" :key="field.key">
                      <div class="spec-field">
                        <label class="spec-label">{{ field.label }}</label>
                        <el-select
                          v-if="field.type === 'select'"
                          v-model="compData[compStep - 1].specs[field.key]"
                          filterable allow-create default-first-option
                          :placeholder="field.placeholder" style="width:100%">
                          <el-option v-for="o in (field.options || [])" :key="o" :label="o" :value="o" />
                        </el-select>
                        <el-input v-else v-model="compData[compStep - 1].specs[field.key]" :placeholder="field.placeholder" />
                      </div>
                    </el-col>
                  </el-row>
                </div>

                <!-- 配件子向导底部按钮 -->
                <div class="comp-footer">
                  <el-button v-if="compStep > 1" @click="compStep--; loadCompData()">上一件</el-button>
                  <el-button type="primary" @click="confirmComponent">
                    {{ compStep < COMPONENTS.length ? '下一件' : '录入完成' }}
                  </el-button>
                </div>
              </div>

              <!-- 汇总面板 -->
              <div v-else class="summary-panel">
                <h4 class="summary-title">已录入配件汇总</h4>
                <div v-for="(comp, i) in COMPONENTS" :key="i" class="summary-item" :class="{ skipped: !compData[i].brand }">
                  <span class="summary-icon">{{ comp.icon }}</span>
                  <span class="summary-label">{{ comp.label }}</span>
                  <span v-if="compData[i].brand" class="summary-value">
                    {{ compData[i].brand }} {{ compData[i].series ? compData[i].series + ' ' : '' }}{{ compData[i].model }}
                  </span>
                  <el-tag v-else size="small" type="info">已跳过</el-tag>
                  <el-button link type="primary" size="small" @click="compStep = i + 1; loadCompData()">编辑</el-button>
                </div>

                <!-- 额外配件 -->
                <div v-if="extraItems.length > 0" class="extra-list">
                  <div class="divider"></div>
                  <h4 class="summary-title">额外配件</h4>
                  <div v-for="(ext, i) in extraItems" :key="i" class="summary-item">
                    <span class="summary-icon">📎</span>
                    <span class="summary-label">{{ ext.type }}</span>
                    <span class="summary-value">{{ ext.brand }} {{ ext.model }}</span>
                    <el-button link type="danger" size="small" @click="extraItems.splice(i, 1)">删除</el-button>
                  </div>
                </div>

                <el-button class="add-extra-btn" @click="showExtraDialog = true">
                  + 添加额外配件（显示器/键盘/鼠标等）
                </el-button>
              </div>
            </template>

            <!-- ========== 笔记本 ========== -->
            <div v-if="form.order_type === '笔记本'" class="spec-box">
              <h4 class="spec-box-title">笔记本详细配置</h4>
              <el-row :gutter="12">
                <el-col :span="12">
                  <div class="spec-field">
                    <label class="spec-label required">品牌</label>
                    <el-select
                      v-model="configForm.laptop_brand"
                      filterable allow-create default-first-option
                      placeholder="搜索或输入品牌" style="width:100%">
                      <el-option v-for="b in laptopBrandOptions" :key="b" :label="b" :value="b" />
                    </el-select>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="spec-field">
                    <label class="spec-label required">系列型号</label>
                    <el-input v-model="configForm.laptop_series" placeholder="如：蛟龙16pro / 拯救者Y9000P" />
                  </div>
                </el-col>
              </el-row>
              <el-row :gutter="12" style="margin-top: 12px">
                <el-col :span="12" v-for="field in laptopFields" :key="field.key">
                  <div class="spec-field">
                    <label class="spec-label">{{ field.label }}</label>
                    <el-input v-model="configForm[field.key]" :placeholder="field.placeholder" />
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- ========== 散件/配件（列表模式） ========== -->
            <template v-if="form.order_type === '散件'">
              <!-- 已添加列表 -->
              <div v-if="partsList.length > 0" class="summary-panel" style="margin-bottom: 16px">
                <h4 class="summary-title">已添加配件（{{ partsList.length }} 件）</h4>
                <div v-for="(p, i) in partsList" :key="i" class="summary-item">
                  <span class="summary-icon">🔧</span>
                  <span class="summary-label">{{ getPartsLabel(p.subType) }}</span>
                  <span class="summary-value">
                    {{ p.brand }} {{ p.series ? p.series + ' ' : '' }}{{ p.model }}
                  </span>
                  <el-button link type="primary" size="small" @click="editPart(i)">编辑</el-button>
                  <el-button link type="danger" size="small" @click="partsList.splice(i, 1)">删除</el-button>
                </div>
              </div>

              <!-- 编辑卡片 -->
              <div v-if="partsEditing" class="comp-card">
                <div class="comp-header">
                  <span class="comp-name">🔧 {{ partsEditIndex >= 0 ? '编辑配件' : '添加新配件' }}</span>
                </div>

                <!-- 分类 -->
                <div class="spec-field">
                  <label class="spec-label required">配件分类</label>
                  <el-select v-model="currentPart.subType" placeholder="请选择分类" style="width:100%"
                    @change="onPartSubTypeChange">
                    <el-option-group label="电脑核心配件">
                      <el-option v-for="s in partsSubOptions.filter(o => !['monitor','keyboard','mouse','headset','other'].includes(o.value))"
                        :key="s.value" :label="s.label" :value="s.value" />
                    </el-option-group>
                    <el-option-group label="外设/其他">
                      <el-option v-for="s in partsSubOptions.filter(o => ['monitor','keyboard','mouse','headset','other'].includes(o.value))"
                        :key="s.value" :label="s.label" :value="s.value" />
                    </el-option-group>
                  </el-select>
                </div>

                <!-- 品牌 -->
                <div class="spec-field">
                  <label class="spec-label">品牌</label>
                  <el-select
                    v-model="currentPart.brand"
                    filterable allow-create default-first-option
                    placeholder="搜索或输入品牌"
                    style="width: 100%"
                    :disabled="!currentPart.subType"
                    @change="onPartBrandChange"
                  >
                    <el-option v-for="b in partBrandOptions" :key="b" :label="b" :value="b" />
                  </el-select>
                </div>

                <!-- 系列（选填） -->
                <div class="spec-field">
                  <label class="spec-label">系列（选填）</label>
                  <el-input v-model="currentPart.series" placeholder="如 ROG / TUF / 巨齿鲨（可留空）" />
                </div>

                <!-- 型号 -->
                <div class="spec-field">
                  <label class="spec-label">型号</label>
                  <el-select
                    v-model="currentPart.model"
                    filterable allow-create default-first-option
                    :disabled="!currentPart.brand"
                    placeholder="搜索或输入型号"
                    style="width: 100%"
                    :loading="partModelLoading"
                    @change="onPartModelChange"
                  >
                    <el-option v-for="m in partModelOptions" :key="m.model_name" :label="m.model_name" :value="m.model_name" />
                  </el-select>
                </div>

                <!-- 动态规格参数 -->
                <div v-if="currentPartSpecFields.length > 0" class="spec-dynamic">
                  <el-row :gutter="12">
                    <el-col :span="12" v-for="field in currentPartSpecFields" :key="field.key">
                      <div class="spec-field">
                        <label class="spec-label">{{ field.label }}</label>
                        <el-select
                          v-if="field.type === 'select'"
                          v-model="currentPart.specs[field.key]"
                          filterable allow-create default-first-option
                          :placeholder="field.placeholder" style="width:100%">
                          <el-option v-for="o in (field.options || [])" :key="o" :label="o" :value="o" />
                        </el-select>
                        <el-input v-else v-model="currentPart.specs[field.key]" :placeholder="field.placeholder" />
                      </div>
                    </el-col>
                  </el-row>
                </div>

                <!-- 备注 -->
                <div class="spec-field">
                  <label class="spec-label">备注</label>
                  <el-input v-model="currentPart.note" placeholder="选填备注" />
                </div>

                <!-- 按钮 -->
                <div class="comp-footer">
                  <el-button @click="cancelPartEdit">取消</el-button>
                  <el-button type="primary" @click="confirmPart">
                    {{ partsEditIndex >= 0 ? '保存修改' : '确认此件' }}
                  </el-button>
                </div>
              </div>

              <!-- 添加按钮 -->
              <el-button v-if="!partsEditing" class="add-extra-btn" @click="startAddPart">
                + 再加一件配件
              </el-button>
            </template>

            <!-- 通用：成色 + 功能状态 + 价格（所有类型共用） -->
            <div class="divider"></div>
            <el-row :gutter="16">
              <el-col :span="12">
                <div class="spec-field">
                  <label class="spec-label">成色鉴定</label>
                  <el-select v-model="form.condition_grade" placeholder="选择成色" style="width: 100%">
                    <el-option label="全新未拆封" value="全新未拆封" />
                    <el-option label="充新 / 仅拆封" value="充新" />
                    <el-option label="轻微使用痕迹" value="轻微使用痕迹" />
                    <el-option label="明显使用痕迹" value="明显使用痕迹" />
                    <el-option label="战损成色" value="战损成色" />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="spec-field">
                  <label class="spec-label">功能状态</label>
                  <el-select v-model="form.functional_status" placeholder="选择状态" style="width: 100%">
                    <el-option label="功能完好无维修" value="功能完好" />
                    <el-option label="维修过，可正常使用" value="维修过可用" />
                    <el-option label="部分功能故障" value="部分故障" />
                    <el-option label="完全损坏" value="完全损坏" />
                  </el-select>
                </div>
              </el-col>
            </el-row>
            <div class="field-block" style="margin-top: 20px">
              <label class="field-title">预估回收价格</label>
              <div class="price-input-big">
                <span class="price-sign">¥</span>
                <el-input-number v-model="form.price" :precision="2" :min="0" :step="100" :controls="false"
                  placeholder="0.00" size="large" class="price-field" />
              </div>
            </div>
          </div>

          <!-- ====== Step 3: 物流结算 ====== -->
          <div v-show="currentStep === 3" class="step-pane">
            <div class="field-block">
              <label class="field-title">1. 卖家发货方式</label>
              <div class="pill-group">
                <span v-for="s in shippingOptions" :key="s.value"
                  class="pill" :class="{ selected: form.shipping_method === s.value }"
                  @click="form.shipping_method = s.value">{{ s.label }}</span>
              </div>
            </div>
            <el-row :gutter="16">
              <el-col :span="12">
                <div class="field-block">
                  <label class="field-title">2. 应付打款金额</label>
                  <div class="price-input-sm">
                    <span class="price-sign-sm">¥</span>
                    <el-input-number v-model="form.payment_amount" :precision="2" :min="0" :step="100" :controls="false" placeholder="0.00" size="large" class="price-field" />
                  </div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="field-block">
                  <label class="field-title">3. 我方承担运费</label>
                  <div class="price-input-sm">
                    <span class="price-sign-sm">¥</span>
                    <el-input-number v-model="form.shipping_fee" :precision="2" :min="0" :step="5" :controls="false" placeholder="包邮填0" size="large" class="price-field" />
                  </div>
                </div>
              </el-col>
            </el-row>
            <div class="field-block">
              <label class="field-title">4. 订单系统状态</label>
              <el-select v-model="form.order_status" style="width: 100%" size="large">
                <el-option label="待收货 / 测试中" value="待收货" />
                <el-option label="测试通过 / 待打款" value="待打款" />
                <el-option label="已打款 / 入库完毕" value="已完成" />
                <el-option label="验机不符 / 退货拦截" value="退货" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- 主向导底部按钮 -->
        <div class="wizard-footer">
          <el-button v-if="currentStep > 1" size="large" round @click="currentStep--" class="btn-back">上一步</el-button>
          <el-button v-if="currentStep < 3" size="large" round type="warning" class="btn-forward" @click="handleNext">
            {{ currentStep === 1 ? '下一步 (填写配置)' : '下一步 (物流结算)' }}
          </el-button>
          <el-button v-else size="large" round type="success" class="btn-forward" :loading="submitLoading" @click="handleSubmit">
            确认入库登记
          </el-button>
        </div>
      </div>
    </div>

    <!-- 额外配件弹窗 -->
    <el-dialog v-model="showExtraDialog" title="添加额外配件" width="420px">
      <el-form label-width="70px">
        <el-form-item label="类型">
          <el-select v-model="extraForm.type" placeholder="选择类型" style="width: 100%" filterable allow-create>
            <el-option label="显示器" value="显示器" />
            <el-option label="键盘" value="键盘" />
            <el-option label="鼠标" value="鼠标" />
            <el-option label="耳机" value="耳机" />
            <el-option label="摄像头" value="摄像头" />
            <el-option label="音箱" value="音箱" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="extraForm.brand" placeholder="如：AOC / 罗技" />
        </el-form-item>
        <el-form-item label="型号">
          <el-input v-model="extraForm.model" placeholder="如：27G2 / G502" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="extraForm.note" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExtraDialog = false">取消</el-button>
        <el-button type="primary" @click="addExtra">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import { createOrder } from '@/api/order'
import { getBrands, getModels, getPropertySchema } from '@/api/sku'
import { ElMessage } from 'element-plus'

// ---- 主向导 ----
const currentStep = ref(1)
const submitLoading = ref(false)
const stepLabels = ['客户', '明细', '结算']
const stepTitles = ['1. 登记客户(卖家)信息', '2. 评估配件明细配置', '3. 财务结算与物流']
const progressWidth = computed(() => `${((currentStep.value - 1) / 2) * 100}%`)
function goToStep(step) { if (step <= currentStep.value) currentStep.value = step }

// ---- 选项数据 ----
const platformOptions = [
  { value: '闲鱼', label: '闲鱼', icon: '🐟' },
  { value: '淘宝', label: '淘宝', icon: '🛒' },
  { value: '微信', label: '微信', icon: '💬' },
  { value: '线下同城', label: '线下同城', icon: '🤝' },
]
const typeOptions = [
  { value: '台式整机', label: '台式整机', icon: '🖥️' },
  { value: '笔记本', label: '笔记本', icon: '💻' },
  { value: '散件', label: '散件/配件', icon: '🔧' },
]
const shippingOptions = [
  { value: '顺丰', label: '顺丰速运' },
  { value: '普通快递', label: '普通快递' },
  { value: '上门自提', label: '上门自提' },
]

// ---- 八大件定义 ----
const COMPONENTS = [
  { key: 'cpu', label: 'CPU 处理器', icon: '🧠', skuCategory: 'CPU' },
  { key: 'gpu', label: '显卡 GPU', icon: '🎮', skuCategory: '显卡' },
  { key: 'motherboard', label: '主板', icon: '🔲', skuCategory: '主板' },
  { key: 'ram', label: '内存', icon: '📊', skuCategory: '内存' },
  { key: 'disk', label: '硬盘', icon: '💾', skuCategory: '硬盘' },
  { key: 'psu', label: '电源', icon: '🔌', skuCategory: '电源' },
  { key: 'cooler', label: '散热器', icon: '❄️', skuCategory: '散热器' },
  { key: 'case', label: '机箱', icon: '📦', skuCategory: '机箱' },
]

function makeEmptyCompData() {
  return COMPONENTS.map(() => ({ brand: '', series: '', model: '', sku_id: null, specs: {} }))
}

const compStep = ref(1)
const compData = ref(makeEmptyCompData())
const brandOptions = ref([])
const modelOptions = ref([])
const modelLoading = ref(false)
const allModelData = ref([])
const specSchemaCache = reactive({})
const currentComp = computed(() => COMPONENTS[compStep.value - 1])

const currentSpecFields = computed(() => {
  if (!currentComp.value) return []
  return specSchemaCache[currentComp.value.skuCategory] || []
})

const extraItems = ref([])
const showExtraDialog = ref(false)
const extraForm = ref({ type: '', brand: '', model: '', note: '' })

// ---- 配件子向导数据加载 ----
async function loadCompData() {
  const cat = currentComp.value.skuCategory
  brandOptions.value = []
  modelOptions.value = []
  allModelData.value = []
  try {
    const res = await getBrands(cat)
    brandOptions.value = res.data || []
  } catch { /* ignore */ }
  if (!specSchemaCache[cat]) {
    try {
      const res = await getPropertySchema(cat)
      specSchemaCache[cat] = (res.data && res.data[cat]) || []
    } catch { /* ignore */ }
  }
  const current = compData.value[compStep.value - 1]
  if (current.brand) {
    await fetchModels(cat, current.brand)
  }
}

async function fetchModels(category, brand) {
  modelLoading.value = true
  try {
    const res = await getModels(category, brand)
    allModelData.value = res.data || []
    modelOptions.value = allModelData.value
  } finally {
    modelLoading.value = false
  }
}

async function onBrandChange(brand) {
  const current = compData.value[compStep.value - 1]
  current.series = ''
  current.model = ''
  current.sku_id = null
  current.specs = {}
  if (brand) {
    await fetchModels(currentComp.value.skuCategory, brand)
  } else {
    modelOptions.value = []
    allModelData.value = []
  }
}

function onModelChange(modelName) {
  const current = compData.value[compStep.value - 1]
  const matched = allModelData.value.find(m => m.model_name === modelName)
  if (matched) {
    current.sku_id = matched.id
    current.specs = { ...(matched.properties || {}) }
  } else {
    current.sku_id = null
  }
}

function skipComponent() {
  const current = compData.value[compStep.value - 1]
  current.brand = ''
  current.series = ''
  current.model = ''
  current.sku_id = null
  current.specs = {}
  if (compStep.value < COMPONENTS.length) {
    compStep.value++
    loadCompData()
  } else {
    compStep.value = COMPONENTS.length + 1
  }
}

function confirmComponent() {
  if (compStep.value < COMPONENTS.length) {
    compStep.value++
    loadCompData()
  } else {
    compStep.value = COMPONENTS.length + 1
  }
}

function onTypeChange(val) {
  form.value.order_type = val
  if (val === '台式整机') {
    compStep.value = 1
    compData.value = makeEmptyCompData()
    extraItems.value = []
    loadCompData()
  } else if (val === '散件') {
    partsList.value = []
    currentPart.value = makeEmptyPart()
    partsEditing.value = true
    partsEditIndex.value = -1
  }
}

function addExtra() {
  if (!extraForm.value.type) { ElMessage.warning('请选择类型'); return }
  extraItems.value.push({ ...extraForm.value })
  extraForm.value = { type: '', brand: '', model: '', note: '' }
  showExtraDialog.value = false
}

// 首次进入 Step 2 时加载第一个配件的数据
watch(currentStep, (val) => {
  if (val === 2 && form.value.order_type === '台式整机') {
    loadCompData()
  }
})

// ---- 笔记本 ----
const configForm = reactive({})
const laptopBrandOptions = [
  '联想', '华硕', '戴尔', '惠普', '机械革命', '神舟', '微星',
  '宏碁', '雷蛇', '外星人', '苹果', '华为', '小米', '荣耀', '三星',
]
const laptopFields = [
  { key: 'laptop_cpu', label: '处理器', placeholder: '如：R7 8945hx' },
  { key: 'laptop_gpu', label: '显卡', placeholder: '如：RTX 4070' },
  { key: 'laptop_ram', label: '内存容量', placeholder: '如：32G DDR5' },
  { key: 'laptop_storage', label: '硬盘存储', placeholder: '如：1T+1T 固态' },
  { key: 'laptop_screen', label: '屏幕规格', placeholder: '如：16寸 2.5K 165Hz' },
]

// ---- 散件/配件列表模式 ----
const partsList = ref([])
const partsEditing = ref(true)
const partsEditIndex = ref(-1)
const currentPart = ref(makeEmptyPart())
const partBrandOptions = ref([])
const partModelOptions = ref([])
const partModelLoading = ref(false)
const allPartModelData = ref([])

function makeEmptyPart() {
  return { subType: '', brand: '', series: '', model: '', sku_id: null, specs: {}, note: '' }
}

function getPartsLabel(subTypeValue) {
  const opt = partsSubOptions.find(o => o.value === subTypeValue)
  return opt ? opt.label : subTypeValue
}

function getPartsSkuCategory(subTypeValue) {
  const opt = partsSubOptions.find(o => o.value === subTypeValue)
  return opt ? opt.skuCategory : ''
}

const currentPartSpecFields = computed(() => {
  const cat = getPartsSkuCategory(currentPart.value.subType)
  if (!cat) return []
  return specSchemaCache[cat] || []
})

async function onPartSubTypeChange() {
  currentPart.value.brand = ''
  currentPart.value.series = ''
  currentPart.value.model = ''
  currentPart.value.sku_id = null
  currentPart.value.specs = {}
  partBrandOptions.value = []
  partModelOptions.value = []
  allPartModelData.value = []
  const cat = getPartsSkuCategory(currentPart.value.subType)
  if (!cat) return
  try {
    const res = await getBrands(cat)
    partBrandOptions.value = res.data || []
  } catch { /* ignore */ }
  if (!specSchemaCache[cat]) {
    try {
      const res = await getPropertySchema(cat)
      specSchemaCache[cat] = (res.data && res.data[cat]) || []
    } catch { /* ignore */ }
  }
}

async function onPartBrandChange(brand) {
  currentPart.value.series = ''
  currentPart.value.model = ''
  currentPart.value.sku_id = null
  currentPart.value.specs = {}
  partModelOptions.value = []
  allPartModelData.value = []
  if (!brand) return
  const cat = getPartsSkuCategory(currentPart.value.subType)
  if (!cat) return
  partModelLoading.value = true
  try {
    const res = await getModels(cat, brand)
    allPartModelData.value = res.data || []
    partModelOptions.value = allPartModelData.value
  } finally {
    partModelLoading.value = false
  }
}

function onPartModelChange(modelName) {
  const matched = allPartModelData.value.find(m => m.model_name === modelName)
  if (matched) {
    currentPart.value.sku_id = matched.id
    currentPart.value.specs = { ...(matched.properties || {}) }
  } else {
    currentPart.value.sku_id = null
  }
}

function confirmPart() {
  if (!currentPart.value.subType) { ElMessage.warning('请选择配件分类'); return }
  const item = { ...currentPart.value, specs: { ...currentPart.value.specs } }
  if (partsEditIndex.value >= 0) {
    partsList.value[partsEditIndex.value] = item
  } else {
    partsList.value.push(item)
  }
  partsEditing.value = false
  partsEditIndex.value = -1
  currentPart.value = makeEmptyPart()
}

function editPart(index) {
  const p = partsList.value[index]
  currentPart.value = { ...p, specs: { ...p.specs } }
  partsEditIndex.value = index
  partsEditing.value = true
  onPartSubTypeChange().then(() => {
    if (p.brand) {
      onPartBrandChange(p.brand).then(() => {
        currentPart.value.brand = p.brand
        currentPart.value.series = p.series
        currentPart.value.model = p.model
        currentPart.value.sku_id = p.sku_id
        currentPart.value.specs = { ...p.specs }
      })
    }
  })
}

function cancelPartEdit() {
  partsEditing.value = false
  partsEditIndex.value = -1
  currentPart.value = makeEmptyPart()
}

function startAddPart() {
  currentPart.value = makeEmptyPart()
  partsEditIndex.value = -1
  partsEditing.value = true
}
const partsSubOptions = [
  { value: 'cpu', label: 'CPU 处理器', skuCategory: 'CPU' },
  { value: 'gpu', label: '电脑显卡', skuCategory: '显卡' },
  { value: 'mb', label: '主板', skuCategory: '主板' },
  { value: 'ram', label: '内存条', skuCategory: '内存' },
  { value: 'disk', label: '硬盘', skuCategory: '硬盘' },
  { value: 'psu', label: '电源', skuCategory: '电源' },
  { value: 'cooler', label: '散热器', skuCategory: '散热器' },
  { value: 'case', label: '机箱', skuCategory: '机箱' },
  { value: 'monitor', label: '显示器', skuCategory: '显示器' },
  { value: 'keyboard', label: '键盘', skuCategory: '键盘' },
  { value: 'mouse', label: '鼠标', skuCategory: '鼠标' },
  { value: 'headset', label: '耳机', skuCategory: '耳机' },
  { value: 'other', label: '其他', skuCategory: '其他' },
]

// ---- 主表单 ----
const form = ref({
  platform: '闲鱼', customer_id: '', phone: '', region: '',
  order_type: '台式整机', condition_grade: '轻微使用痕迹', functional_status: '功能完好',
  price: 0, shipping_method: '顺丰', payment_amount: 0, shipping_fee: 0, order_status: '待收货',
})

function handleNext() {
  if (currentStep.value === 1 && !form.value.customer_id) {
    ElMessage.warning('请填写卖家ID')
    return
  }
  if (currentStep.value === 2 && form.value.order_type === '台式整机' && compStep.value <= COMPONENTS.length) {
    ElMessage.warning('请先完成所有配件的录入（可跳过不需要的）')
    return
  }
  if (currentStep.value === 2 && form.value.order_type === '散件') {
    if (partsEditing.value && currentPart.value.subType) {
      ElMessage.warning('当前有未保存的配件，请先确认或取消')
      return
    }
    if (partsList.value.length === 0 && !currentPart.value.subType) {
      ElMessage.warning('请至少添加一件配件')
      return
    }
  }
  currentStep.value++
}

// ---- 提交 ----
function buildConfigDetail() {
  const type = form.value.order_type
  if (type === '台式整机') {
    const components = COMPONENTS.map((comp, i) => {
      const d = compData.value[i]
      if (!d.brand) return null
      return { type: comp.skuCategory, brand: d.brand, series: d.series, model: d.model, specs: d.specs }
    }).filter(Boolean)
    const extras = extraItems.value.map(e => ({ type: e.type, brand: e.brand, model: e.model, note: e.note }))
    return JSON.stringify({ components, extras })
  }
  if (type === '笔记本') {
    return JSON.stringify({
      brand: configForm.laptop_brand || '',
      series: configForm.laptop_series || '',
      cpu: configForm.laptop_cpu || '',
      gpu: configForm.laptop_gpu || '',
      ram: configForm.laptop_ram || '',
      storage: configForm.laptop_storage || '',
      screen: configForm.laptop_screen || '',
    })
  }
  if (type === '散件') {
    return JSON.stringify(partsList.value.map(p => ({
      type: getPartsLabel(p.subType),
      skuCategory: getPartsSkuCategory(p.subType),
      brand: p.brand,
      series: p.series,
      model: p.model,
      specs: p.specs,
      note: p.note,
    })))
  }
  return ''
}

function resetAll() {
  form.value = {
    platform: '闲鱼', customer_id: '', phone: '', region: '',
    order_type: '台式整机', condition_grade: '轻微使用痕迹', functional_status: '功能完好',
    price: 0, shipping_method: '顺丰', payment_amount: 0, shipping_fee: 0, order_status: '待收货',
  }
  compStep.value = 1
  compData.value = makeEmptyCompData()
  extraItems.value = []
  Object.keys(configForm).forEach(k => delete configForm[k])
  partsList.value = []
  partsEditing.value = true
  partsEditIndex.value = -1
  currentPart.value = makeEmptyPart()
  currentStep.value = 1
}

async function handleSubmit() {
  submitLoading.value = true
  try {
    const payload = { ...form.value, config_detail: buildConfigDetail() }
    await createOrder(payload)
    ElMessage.success('入库登记成功！')
    resetAll()
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.receiving-page { min-height: calc(100vh - 120px); display: flex; align-items: flex-start; justify-content: center; padding-top: 12px; }
.wizard-wrapper { width: 100%; max-width: 640px; }
.wizard-card { background: #fff; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); overflow: hidden; display: flex; flex-direction: column; }

.wizard-header { padding: 24px 28px 16px; border-bottom: 1px solid #f0f0f0; }
.wizard-title { font-size: 17px; font-weight: 700; color: #333; margin-bottom: 18px; }
.progress-bar { position: relative; }
.progress-track { position: absolute; top: 14px; left: 30px; right: 30px; height: 3px; background: #e8e8e8; border-radius: 2px; z-index: 0; }
.progress-fill { height: 100%; background: #FFDA44; border-radius: 2px; transition: width 0.35s ease; }
.progress-dots { display: flex; justify-content: space-between; position: relative; z-index: 1; }
.dot-item { display: flex; flex-direction: column; align-items: center; cursor: pointer; }
.dot-circle { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; background: #e8e8e8; color: #999; transition: all 0.25s; }
.dot-item.active .dot-circle { background: #FFDA44; color: #333; }
.dot-item.current .dot-circle { box-shadow: 0 0 0 4px rgba(255,218,68,0.3); }
.dot-text { margin-top: 5px; font-size: 11px; color: #bbb; font-weight: 500; transition: color 0.25s; }
.dot-item.active .dot-text { color: #333; font-weight: 600; }

.wizard-body { padding: 24px 28px; flex: 1; overflow-y: auto; max-height: calc(100vh - 340px); }
.step-pane { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.field-block { margin-bottom: 22px; }
.field-title { display: block; font-size: 13px; font-weight: 700; color: #333; margin-bottom: 10px; }
.divider { height: 1px; background: #f0f0f0; margin: 16px 0; }

.pill-group { display: flex; flex-wrap: wrap; gap: 10px; }
.pill { display: inline-block; padding: 9px 20px; background: #f5f7fa; color: #333; border-radius: 999px; font-size: 13px; cursor: pointer; transition: all 0.2s; border: 1.5px solid transparent; user-select: none; }
.pill:hover { background: #eef1f6; }
.pill.selected { background: #FFF9E6; color: #D48806; border-color: #FFDA44; font-weight: 700; }

/* ---- Component Card (子向导) ---- */
.comp-card { background: #fafafa; border-radius: 12px; border: 1px solid #f0f0f0; padding: 20px; }
.comp-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.comp-progress { display: flex; align-items: center; gap: 10px; }
.comp-idx { background: #FFDA44; color: #333; font-weight: 700; font-size: 12px; padding: 3px 10px; border-radius: 999px; }
.comp-name { font-size: 16px; font-weight: 700; color: #333; }
.comp-progress-bar { height: 4px; background: #e8e8e8; border-radius: 2px; margin-bottom: 20px; }
.comp-progress-fill { height: 100%; background: #FFDA44; border-radius: 2px; transition: width 0.3s; }
.spec-dynamic { margin-top: 8px; padding: 14px; background: #f0f2f5; border-radius: 8px; }
.comp-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; padding-top: 14px; border-top: 1px solid #eee; }

/* ---- Summary Panel ---- */
.summary-panel { animation: fadeIn 0.3s ease; }
.summary-title { font-size: 14px; font-weight: 700; color: #333; margin-bottom: 12px; }
.summary-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; background: #fafafa; border-radius: 8px; margin-bottom: 8px; }
.summary-item.skipped { opacity: 0.5; }
.summary-icon { font-size: 18px; width: 24px; text-align: center; }
.summary-label { font-size: 13px; font-weight: 600; color: #555; width: 80px; }
.summary-value { flex: 1; font-size: 13px; color: #333; }
.add-extra-btn { width: 100%; margin-top: 12px; border-style: dashed; height: 44px; font-size: 14px; }
.extra-list { margin-top: 4px; }

/* ---- Spec boxes (笔记本/散件) ---- */
.spec-box { background: #fafafa; padding: 16px; border-radius: 12px; border: 1px solid #f0f0f0; }
.spec-box-title { font-size: 13px; font-weight: 700; color: #333; margin-bottom: 14px; }
.spec-field { margin-bottom: 12px; }
.spec-field.highlight :deep(.el-input__wrapper) { border: 1px solid #409EFF; }
.spec-label { display: block; font-size: 12px; color: #666; margin-bottom: 4px; font-weight: 500; }
.spec-label.required::after { content: ' *'; color: #F56C6C; }
.sub-spec { margin-top: 12px; padding: 12px; background: #f5f5f5; border-radius: 8px; border: 1px solid #eee; }

/* ---- Price ---- */
.price-input-big { display: flex; align-items: center; background: #f5f7fa; border-radius: 10px; padding-left: 16px; overflow: hidden; }
.price-sign { font-size: 20px; font-weight: 700; color: #333; }
.price-input-sm { display: flex; align-items: center; background: #f5f7fa; border-radius: 10px; padding-left: 12px; overflow: hidden; }
.price-sign-sm { font-size: 15px; font-weight: 600; color: #666; }
.price-field { flex: 1; width: 100%; }
.price-field :deep(.el-input__wrapper) { box-shadow: none !important; background: transparent; }
.price-input-big .price-field :deep(.el-input__inner) { font-size: 22px; font-weight: 700; color: #F56C6C; }
.price-input-sm .price-field :deep(.el-input__inner) { font-size: 16px; font-weight: 600; color: #333; }

/* ---- Footer ---- */
.wizard-footer { display: flex; gap: 12px; padding: 16px 28px; border-top: 1px solid #f0f0f0; background: #fff; }
.btn-back { flex: 1; height: 46px; }
.btn-forward { flex: 2; height: 46px; font-size: 15px; font-weight: 600; }
</style>
