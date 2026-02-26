<template>
  <div class="page-container">
    <div class="page-header">
      <h2>库位管理</h2>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
        新增库位
      </el-button>
    </div>

    <!-- 库位列表 -->
    <el-card shadow="never">
      <el-table :data="locationList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="location_code" label="库位编码" width="160" />
        <el-table-column prop="location_name" label="库位名称" />
        <el-table-column prop="parent_id" label="父级ID" width="100">
          <template #default="{ row }">{{ row.parent_id || '顶级' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除此库位吗？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="showCreateDialog" :title="editingId ? '编辑库位' : '新增库位'" width="480px">
      <el-form :model="formData" label-width="90px">
        <el-form-item label="库位编码" required>
          <el-input v-model="formData.location_code" placeholder="例如：A-1-01" />
        </el-form-item>
        <el-form-item label="库位名称">
          <el-input v-model="formData.location_name" placeholder="例如：显卡良品区" />
        </el-form-item>
        <el-form-item label="父级库位">
          <el-select v-model="formData.parent_id" placeholder="无（顶级库位）" clearable style="width: 100%">
            <el-option
              v-for="loc in locationList"
              :key="loc.id"
              :label="`${loc.location_code} - ${loc.location_name || ''}`"
              :value="loc.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { getLocationList, createLocation, updateLocation, deleteLocation } from '@/api/location'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const submitLoading = ref(false)
const showCreateDialog = ref(false)
const editingId = ref(null)
const locationList = ref([])

const formData = ref({ location_code: '', location_name: '', parent_id: null })

async function fetchList() {
  loading.value = true
  try {
    const res = await getLocationList()
    locationList.value = res.data || []
  } finally {
    loading.value = false
  }
}

function handleEdit(row) {
  editingId.value = row.id
  formData.value = {
    location_code: row.location_code,
    location_name: row.location_name,
    parent_id: row.parent_id,
  }
  showCreateDialog.value = true
}

function closeDialog() {
  showCreateDialog.value = false
  editingId.value = null
  formData.value = { location_code: '', location_name: '', parent_id: null }
}

async function handleSubmit() {
  if (!formData.value.location_code) {
    ElMessage.warning('请填写库位编码')
    return
  }
  submitLoading.value = true
  try {
    if (editingId.value) {
      await updateLocation(editingId.value, formData.value)
      ElMessage.success('更新成功')
    } else {
      await createLocation(formData.value)
      ElMessage.success('创建成功')
    }
    closeDialog()
    fetchList()
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteLocation(id)
    ElMessage.success('删除成功')
    fetchList()
  } catch {
    // 错误已在拦截器中处理
  }
}

onMounted(fetchList)
</script>
