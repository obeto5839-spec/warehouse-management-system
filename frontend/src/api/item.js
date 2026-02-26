import request from '@/utils/request'

export function createItem(data) {
  return request.post('/items/create', data)
}

export function getItemDetail(itemSn) {
  return request.get(`/items/detail/${itemSn}`)
}
