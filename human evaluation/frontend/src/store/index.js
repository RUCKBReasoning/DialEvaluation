import { defineStore } from 'pinia'

export const useStore = defineStore('main', {
  state: () => {
    return {
      annotatorId: '',    // 账号
      annotatorName: '',  // 用户名
      hasLogin: false,    // 登陆状态
    }
  },
  getters: {},
  actions: {},
})