import request from '@/utils/request'

export function createSku(data) {
  return request.post('/skus/create', data)
}

export function searchSkus(params) {
  return request.get('/skus/search', { params })
}

export function autocompleteSku(keyword) {
  return request.get('/skus/autocomplete', { params: { keyword } })
}

export function getCategories() {
  return request.get('/skus/categories')
}

export function getBrands(category) {
  return request.get('/skus/brands', { params: { category } })
}

export function getModels(category, brand) {
  return request.get('/skus/models', { params: { category, brand } })
}

export function getPropertySchema(category) {
  const params = category ? { category } : {}
  return request.get('/skus/property-schema', { params })
}
