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

            <!-- ========== 台式整机：智能清单式录入 ========== -->
            <template v-if="form.order_type === '台式整机'">
              <div class="line-list-section">
                <h4 class="line-list-title">📋 台式配置清单（输入关键词自动匹配）</h4>
                <div class="line-list">
                  <div v-for="(comp, i) in COMPONENTS" :key="comp.key" class="line-input-group"
                    :class="{ 'line-matched': lineMatchedSku[comp.key] }">
                    <span class="line-label">{{ comp.shortLabel }}</span>
                    <span class="line-divider"></span>
                    <el-select
                      v-model="lineInputs[comp.key]"
                      filterable
                      allow-create
                      default-first-option
                      remote
                      :remote-method="(q) => onLineSearch(comp.key, comp.skuCategory, q)"
                      :loading="lineSearchLoading[comp.key]"
                      :placeholder="comp.placeholder"
                      style="flex:1"
                      class="line-select-input"
                      @change="(val) => onLineSelect(comp.key, val)"
                      @clear="onLineClear(comp.key)"
                      clearable
                      :reserve-keyword="false"
                    >
                      <el-option
                        v-for="opt in lineSuggestions[comp.key]"
                        :key="opt.id"
                        :label="opt.label"
                        :value="opt.label"
                      >
                        <div class="suggestion-item">
                          <span class="suggestion-brand">{{ opt.brand }}</span>
                          <span class="suggestion-model">{{ opt.series ? opt.series + ' ' : '' }}{{ opt.model_name }}</span>
                        </div>
                      </el-option>
                    </el-select>
                    <span v-if="lineMatchedSku[comp.key]" class="line-match-badge">✓ 已匹配</span>
                  </div>

                  <!-- 动态添加的额外配件行 -->
                  <div v-for="(extra, i) in extraLineItems" :key="'extra-' + i" class="line-input-group">
                    <select v-model="extra.type" class="line-type-select">
                      <option value="显示器">显示器</option>
                      <option value="风扇">风扇</option>
                      <option value="键盘">键盘</option>
                      <option value="鼠标">鼠标</option>
                      <option value="耳机">耳机</option>
                      <option value="其他">其他</option>
                    </select>
                    <span class="line-divider"></span>
                    <el-select
                      v-model="extra.desc"
                      filterable
                      allow-create
                      default-first-option
                      remote
                      :remote-method="(q) => onExtraLineSearch(i, extra.type, q)"
                      :loading="extra._loading"
                      placeholder="输入型号及描述"
                      style="flex:1"
                      class="line-select-input"
                      clearable
                      :reserve-keyword="false"
                    >
                      <el-option
                        v-for="opt in (extra._suggestions || [])"
                        :key="opt.id"
                        :label="opt.label"
                        :value="opt.label"
                      >
                        <div class="suggestion-item">
                          <span class="suggestion-brand">{{ opt.brand }}</span>
                          <span class="suggestion-model">{{ opt.series ? opt.series + ' ' : '' }}{{ opt.model_name }}</span>
                        </div>
                      </el-option>
                    </el-select>
                    <button class="line-remove-btn" @click="extraLineItems.splice(i, 1)">&times;</button>
                  </div>
                </div>

                <!-- 添加额外配件按钮 -->
                <button class="line-add-btn" @click="addExtraLine">
                  <span class="line-add-icon">+</span> 添加其他配件（如风扇、显示器、外设等）
                </button>
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
                    {{ p.brand }}{{ p.series ? ' ' + p.series : '' }}{{ p.model ? ' ' + p.model : '' }}{{ p.spec ? ' ' + p.spec : '' }}
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

                <!-- 型号（智能搜索，输入关键词自动匹配并回填品牌/系列） -->
                <div class="spec-field">
                  <label class="spec-label">型号 <span style="color:#999;font-weight:400">（输入关键词搜索，如 12700、4060Ti）</span></label>
                  <el-select
                    v-model="currentPart.model"
                    filterable allow-create default-first-option
                    remote
                    :remote-method="onPartModelSearch"
                    :disabled="!currentPart.subType"
                    placeholder="输入型号关键词搜索..."
                    style="width: 100%"
                    :loading="partModelLoading"
                    @change="onPartModelSelect"
                    clearable
                    :reserve-keyword="false"
                  >
                    <el-option
                      v-for="m in partModelOptions"
                      :key="m.id"
                      :label="m.label"
                      :value="m.model_name"
                    >
                      <div class="suggestion-item">
                        <span class="suggestion-brand">{{ m.brand }}</span>
                        <span class="suggestion-model">{{ m.series ? m.series + ' ' : '' }}{{ m.model_name }}</span>
                      </div>
                    </el-option>
                  </el-select>
                </div>

                <!-- 品牌（自动回填或手动输入） -->
                <div class="spec-field">
                  <label class="spec-label">品牌 <span v-if="currentPart.sku_id" style="color:#16a34a;font-size:11px">✓ 已自动填入</span></label>
                  <el-select
                    v-model="currentPart.brand"
                    filterable allow-create default-first-option
                    placeholder="搜索或输入品牌（选型号后自动填入）"
                    style="width: 100%"
                    :disabled="!currentPart.subType"
                  >
                    <el-option v-for="b in partBrandOptions" :key="b" :label="b" :value="b" />
                  </el-select>
                </div>

                <!-- 系列（自动回填或手动输入） -->
                <div class="spec-field">
                  <label class="spec-label">系列（选填） <span v-if="currentPart.sku_id && currentPart.series" style="color:#16a34a;font-size:11px">✓ 已自动填入</span></label>
                  <el-input v-model="currentPart.series" placeholder="如 雪豹 / 酷睿 / ROG STRIX / 凌霜（可留空）" />
                </div>

                <!-- 规格（简化的文本输入） -->
                <div v-if="currentPartSpecFields.length > 0" class="spec-dynamic">
                  <el-row :gutter="12">
                    <el-col :span="currentPartSpecFields.length === 1 ? 24 : 12" v-for="field in currentPartSpecFields" :key="field.key">
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

            <!-- 通用：备注（所有类型共用） -->
            <div class="divider"></div>
            <div class="field-block">
              <label class="field-title">备注</label>
              <el-input
                v-model="form.remark"
                type="textarea"
                :rows="3"
                placeholder="填写整机/散件的成色、问题描述等备注信息"
              />
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
                <el-option label="已打款，在途中" value="已打款，在途中" />
                <el-option label="未打款，在途中" value="未打款，在途中" />
                <el-option label="已打款，入库完毕" value="已打款，入库完毕" />
                <el-option label="验机不符，退货拦截" value="验机不符，退货拦截" />
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
import { getBrands, getModels, getPropertySchema, searchSkus } from '@/api/sku'
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
  { value: '淘宝', label: '淘宝', icon: '🛒' },
  { value: '闲鱼', label: '闲鱼', icon: '🐟' },
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
  { key: 'cpu', label: 'CPU 处理器', shortLabel: 'CPU', icon: '🧠', skuCategory: 'CPU', placeholder: '如：英特尔 酷睿 i5-13490F' },
  { key: 'gpu', label: '显卡 GPU', shortLabel: '显卡', icon: '🎮', skuCategory: '显卡', placeholder: '如：华硕 雪豹 RTX 4060 Ti O16G' },
  { key: 'motherboard', label: '主板', shortLabel: '主板', icon: '🔲', skuCategory: '主板', placeholder: '如：华硕 ROG STRIX B760I GAMING WIFI-D5' },
  { key: 'ram', label: '内存', shortLabel: '内存', icon: '📊', skuCategory: '内存', placeholder: '如：宏碁 凌霜 32G(16*2)6400C32 海力士A-DIE' },
  { key: 'disk', label: '硬盘', shortLabel: '固态', icon: '💾', skuCategory: '硬盘', placeholder: '如：宏碁 掠夺者GM7 1TB PCIE4.0 7200M/S' },
  { key: 'psu', label: '电源', shortLabel: '电源', icon: '🔌', skuCategory: '电源', placeholder: '如：联力 SFX 750W 金牌全模黑色' },
  { key: 'cooler', label: '散热器', shortLabel: '散热', icon: '❄️', skuCategory: '散热器', placeholder: '如：乔思伯 CR1400' },
  { key: 'case', label: '机箱', shortLabel: '机箱', icon: '📦', skuCategory: '机箱', placeholder: '如：机械大师 C24小方糖 银色' },
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

// ---- 台式整机：清单式单行录入数据 ----
function makeEmptyLineInputs() {
  const obj = {}
  COMPONENTS.forEach(c => { obj[c.key] = '' })
  return obj
}
const lineInputs = reactive(makeEmptyLineInputs())
const extraLineItems = ref([])

function addExtraLine() {
  extraLineItems.value.push({ type: '其他', desc: '', _loading: false, _suggestions: [] })
}

// ---- 台式整机：智能搜索状态 ----
const lineSuggestions = reactive({})
const lineSearchLoading = reactive({})
const lineMatchedSku = reactive({})
const lineSearchCache = reactive({}) // 缓存搜索结果中的原始SKU数据
COMPONENTS.forEach(c => {
  lineSuggestions[c.key] = []
  lineSearchLoading[c.key] = false
  lineMatchedSku[c.key] = false
  lineSearchCache[c.key] = []
})

// 防抖定时器
const lineSearchTimers = {}

async function onLineSearch(compKey, skuCategory, query) {
  // 清除之前的定时器
  if (lineSearchTimers[compKey]) clearTimeout(lineSearchTimers[compKey])
  if (!query || query.length < 1) {
    lineSuggestions[compKey] = []
    return
  }
  lineSearchLoading[compKey] = true
  // 300ms 防抖
  lineSearchTimers[compKey] = setTimeout(async () => {
    try {
      const res = await searchSkus({ category: skuCategory, keyword: query, limit: 15 })
      const items = res.data || []
      lineSearchCache[compKey] = items
      lineSuggestions[compKey] = items.map(s => ({
        id: s.id,
        brand: s.brand,
        series: s.series || '',
        model_name: s.model_name,
        label: `${s.brand}${s.series ? ' ' + s.series : ''} ${s.model_name}`,
        properties: s.properties,
      }))
    } catch {
      lineSuggestions[compKey] = []
    } finally {
      lineSearchLoading[compKey] = false
    }
  }, 300)
}

function onLineSelect(compKey, val) {
  // 检查是否匹配了某个建议项
  const matched = lineSuggestions[compKey].find(s => s.label === val)
  lineMatchedSku[compKey] = !!matched
}

function onLineClear(compKey) {
  lineMatchedSku[compKey] = false
  lineSuggestions[compKey] = []
}

// 额外配件行的搜索
const extraSearchTimers = {}
async function onExtraLineSearch(index, type, query) {
  const extra = extraLineItems.value[index]
  if (!extra) return
  if (extraSearchTimers[index]) clearTimeout(extraSearchTimers[index])
  if (!query || query.length < 1) {
    extra._suggestions = []
    return
  }
  extra._loading = true
  extraSearchTimers[index] = setTimeout(async () => {
    try {
      const res = await searchSkus({ category: type, keyword: query, limit: 10 })
      const items = res.data || []
      extra._suggestions = items.map(s => ({
        id: s.id,
        brand: s.brand,
        series: s.series || '',
        model_name: s.model_name,
        label: `${s.brand}${s.series ? ' ' + s.series : ''} ${s.model_name}`,
      }))
    } catch {
      extra._suggestions = []
    } finally {
      extra._loading = false
    }
  }, 300)
}

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
    current.series = matched.series || ''
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
    // 重置清单式录入数据
    COMPONENTS.forEach(c => { lineInputs[c.key] = '' })
    extraLineItems.value = []
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
  return { subType: '', brand: '', series: '', model: '', sku_id: null, specs: {}, spec: '', note: '' }
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

// 散件：型号远程搜索（输入关键词 → 搜索该分类下的SKU → 显示建议）
let partModelSearchTimer = null
function onPartModelSearch(query) {
  if (partModelSearchTimer) clearTimeout(partModelSearchTimer)
  if (!query || query.length < 1) {
    partModelOptions.value = []
    return
  }
  const cat = getPartsSkuCategory(currentPart.value.subType)
  if (!cat) return
  partModelLoading.value = true
  partModelSearchTimer = setTimeout(async () => {
    try {
      const res = await searchSkus({ category: cat, keyword: query, limit: 15 })
      const items = res.data || []
      allPartModelData.value = items
      partModelOptions.value = items.map(s => ({
        id: s.id,
        brand: s.brand,
        series: s.series || '',
        model_name: s.model_name,
        label: `${s.brand}${s.series ? ' ' + s.series : ''} ${s.model_name}`,
        properties: s.properties,
      }))
    } catch {
      partModelOptions.value = []
    } finally {
      partModelLoading.value = false
    }
  }, 300)
}

// 散件：选中型号后自动回填品牌、系列、规格
function onPartModelSelect(modelName) {
  const matched = partModelOptions.value.find(m => m.model_name === modelName)
  if (matched) {
    currentPart.value.sku_id = matched.id
    currentPart.value.brand = matched.brand
    currentPart.value.series = matched.series || ''
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
  // 加载该分类的品牌列表和规格定义
  onPartSubTypeChange().then(() => {
    // 恢复编辑数据（onPartSubTypeChange 会清空，所以需要重新赋值）
    currentPart.value.brand = p.brand
    currentPart.value.series = p.series
    currentPart.value.model = p.model
    currentPart.value.sku_id = p.sku_id
    currentPart.value.specs = { ...p.specs }
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
  platform: '淘宝', customer_id: '', phone: '', region: '',
  order_type: '台式整机', remark: '',
  price: 0, shipping_method: '顺丰', payment_amount: 0, shipping_fee: 0, order_status: '未打款，在途中',
})

function handleNext() {
  if (currentStep.value === 1 && !form.value.customer_id) {
    ElMessage.warning('请填写卖家ID')
    return
  }
  // 台式整机清单模式无需额外校验，直接放行
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
    const components = COMPONENTS.map(comp => {
      const desc = lineInputs[comp.key]
      if (!desc || !desc.trim()) return null
      return { type: comp.skuCategory, label: comp.shortLabel, description: desc.trim() }
    }).filter(Boolean)
    const extras = extraLineItems.value
      .filter(e => e.desc && e.desc.trim())
      .map(e => ({ type: e.type, description: e.desc.trim() }))
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
    platform: '淘宝', customer_id: '', phone: '', region: '',
    order_type: '台式整机', remark: '',
    price: 0, shipping_method: '顺丰', payment_amount: 0, shipping_fee: 0, order_status: '未打款，在途中',
  }
  compStep.value = 1
  compData.value = makeEmptyCompData()
  extraItems.value = []
  COMPONENTS.forEach(c => { lineInputs[c.key] = '' })
  extraLineItems.value = []
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
    const { remark, ...rest } = form.value
    const payload = { ...rest, notes: remark, config_detail: buildConfigDetail() }
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

/* ---- 清单式单行录入 ---- */
.line-list-section { animation: fadeIn 0.3s ease; }
.line-list-title { font-size: 14px; font-weight: 700; color: #333; margin-bottom: 12px; }
.line-list { display: flex; flex-direction: column; gap: 8px; }
.line-input-group {
  display: flex; align-items: center; background: #f5f7fa;
  border: 1px solid transparent; border-radius: 8px; padding: 8px 12px;
  transition: all 0.2s;
}
.line-input-group:focus-within {
  border-color: #FFDA44; background: #fff; box-shadow: 0 0 0 2px rgba(255,218,68,0.2);
}
.line-label {
  width: 3.5rem; text-align: center; font-size: 13px; font-weight: 700;
  color: #4B5563; flex-shrink: 0;
}
.line-divider {
  width: 1px; height: 16px; background: #D1D5DB; margin: 0 10px; flex-shrink: 0;
}
.line-input {
  flex: 1; background: transparent; border: none; outline: none;
  font-size: 13px; color: #111827; padding: 4px 0;
}
.line-input::placeholder { color: #9CA3AF; }
.line-select {
  width: 3.5rem; text-align: center; font-size: 13px; font-weight: 700;
  color: #4B5563; background: transparent; border: none; outline: none;
  cursor: pointer; appearance: none; -webkit-appearance: none; flex-shrink: 0;
}
.line-remove-btn {
  background: none; border: none; color: #9CA3AF; font-size: 18px; font-weight: 700;
  cursor: pointer; padding: 0 4px; line-height: 1; transition: color 0.2s;
}
.line-remove-btn:hover { color: #F56C6C; }
.line-add-btn {
  width: 100%; margin-top: 10px; padding: 12px; border: 1px dashed #D1D5DB;
  border-radius: 8px; background: transparent; color: #9CA3AF; font-size: 13px;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;
  transition: all 0.2s;
}
.line-add-btn:hover { background: #f9fafb; color: #6B7280; border-color: #9CA3AF; }
.line-add-btn:active { background: #f0f0f0; }
.line-add-icon { font-size: 16px; line-height: 1; }

/* ---- 智能搜索下拉样式 ---- */
.line-select-input { flex: 1; }
.line-select-input :deep(.el-input__wrapper) {
  box-shadow: none !important; background: transparent; padding: 0;
}
.line-select-input :deep(.el-input__inner) {
  font-size: 13px; color: #111827;
}
.line-select-input :deep(.el-input__suffix) { right: 0; }
.line-input-group.line-matched {
  background: #f0fdf4; border-color: #86efac;
}
.line-match-badge {
  font-size: 11px; color: #16a34a; font-weight: 600;
  white-space: nowrap; margin-left: 6px; flex-shrink: 0;
}
.suggestion-item {
  display: flex; align-items: center; gap: 8px; font-size: 13px;
}
.suggestion-brand {
  color: #6B7280; font-weight: 600; flex-shrink: 0;
}
.suggestion-model {
  color: #111827; flex: 1;
}
.line-type-select {
  width: 4rem; text-align: center; font-size: 13px; font-weight: 700;
  color: #4B5563; background: transparent; border: none; outline: none;
  cursor: pointer; flex-shrink: 0;
}

/* ---- Footer ---- */
.wizard-footer { display: flex; gap: 12px; padding: 16px 28px; border-top: 1px solid #f0f0f0; background: #fff; }
.btn-back { flex: 1; height: 46px; }
.btn-forward { flex: 2; height: 46px; font-size: 15px; font-weight: 600; }
</style>
