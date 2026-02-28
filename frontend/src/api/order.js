import request from '@/utils/request'

export function createOrder(data) {
  return request.post('/orders/create', data)
}

export function getOrders(params) {
  return request.get('/orders/list', { params })
}

export function getOrder(id) {
  return request.get(`/orders/${id}`)
}

export function updateOrder(id, data) {
  return request.put(`/orders/${id}`, data)
}

export function deleteOrder(id) {
  return request.delete(`/orders/${id}`)
}

export function getOrderStats() {
  return request.get('/orders/stats')
}
