import request from '@/utils/request'

export function shelveItem(data) {
  return request.post('/inventory/shelve', data)
}

export function pickItem(data) {
  return request.post('/inventory/pick', data)
}

export function getLocationItems(locationCode) {
  return request.get(`/inventory/location/${locationCode}`)
}

export function getInventoryList(params) {
  return request.get('/inventory/list', { params })
}
