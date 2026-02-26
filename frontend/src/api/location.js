import request from '@/utils/request'

export function createLocation(data) {
  return request.post('/locations/create', data)
}

export function getLocationList(params) {
  return request.get('/locations/list', { params })
}

export function getLocationDetail(id) {
  return request.get(`/locations/detail/${id}`)
}

export function getLocationByCode(code) {
  return request.get(`/locations/code/${code}`)
}

export function updateLocation(id, data) {
  return request.put(`/locations/update/${id}`, data)
}

export function deleteLocation(id) {
  return request.delete(`/locations/delete/${id}`)
}
