import request from '@/utils/request'

export function getMachineItems(machineSn) {
  return request.get(`/machine/items/${machineSn}`)
}

export function shipMachine(data) {
  return request.post('/machine/ship', data)
}

export function unbindAndSell(data) {
  return request.post('/machine/unbind-sell', data)
}

export function checkBinding(itemSn) {
  return request.get(`/machine/check/${itemSn}`)
}
