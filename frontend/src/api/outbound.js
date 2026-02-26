import request from '@/utils/request'

export function createShipping(data) {
  return request.post('/outbound/ship', data)
}

export function getOrderDetail(orderNo) {
  return request.get(`/outbound/detail/${orderNo}`)
}

export function getOutboundList(params) {
  return request.get('/outbound/list', { params })
}
