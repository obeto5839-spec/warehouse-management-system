import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截器：自动加 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('x-token') || 'warehouse-secret-token'
    config.headers['x-token'] = token
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理业务错误
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 业务层错误码处理
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || '操作失败')
      return Promise.reject(new Error(res.message || '操作失败'))
    }
    return res
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
