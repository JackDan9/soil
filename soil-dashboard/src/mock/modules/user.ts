import Mock from 'mockjs'
import { Config } from '../config';
import { getURLParams } from '@/utils/core';

const loginData = Mock.mock({
  token: '@lower(@guid)'
})

const userInfo = Mock.mock({
  name: '@cname',
  username: '@cname',
  nickname: '@cname',
  gender: '@pick([1, 2])',
  avatar: 'https://avatars1.githubusercontent.com/u/12805846?s=60&v=4',
  email: '@email',
  mobilePhone: /^1[345789]\d{9}$/,
  // roles: [1],
  // 路由权限表
  // 如果配置了一级路由，则它之下的所有子路由都可访问。
})

export default {
  login(config: Config) {
    const user = JSON.parse(config.body)
    if ((user.username === 'admin' && user.password === 'passw0rd') || (user.username === 'admin@example.org' && user.password === 'passw0rd')) {
      loginData.token = 'd02fd62b-cfdf-9efb-adfb-7fc1e85bf99c'
    } else if ((user.username === 'guest' && user.password === 'passw0rd') || (user.username === 'guest@example.org' && user.password === 'passw0rd')) {
      loginData.token = 'ecfe1e6b-cba6-dfee-fdba-12015b7f2420'
    } else {
      loginData.token = '6f81bbab-5b7e-abfb-bd44-efd5aeee82cc'
    }
    return {
      code: 0,
      data: loginData
    }
  },
  logout() {
    return {
      code: 0,
      data: {}
    }
  },
  getUserInfo(config: Config) {
    const { token } = getURLParams(config.url)
    if (token === 'd02fd62b-cfdf-9efb-adfb-7fc1e85bf99c') {
      userInfo.permission = [
        {
          id: 1,
          name: 'dashboard',
          discriptiong: '首页',
          reminder: '您没有权限访问首页'
        },
        {
          id: 2,
          name: 'vmware'
        },
        {
          id: 3,
          name: 'openstack'
        },
        {
          id: 4,
          name: 'account'
        }
      ]
    } else if (token === 'ecfe1e6b-cba6-dfee-fdba-12015b7f2420') {
      userInfo.permission = [
        {
          id: 1,
          name: 'dashboard',
          discriptiong: '首页',
          reminder: '您没有权限访问首页'
        },
      ]
    } else {
      userInfo.permission = [
        {
          id: 1,
          name: 'dashboard',
          discriptiong: '首页',
          reminder: '您没有权限访问首页'
        },
        {
          id: 2,
          name: 'vmware'
        },
        {
          id: 3,
          name: 'openstack'
        }
      ]
    }
    return {
      code: 0,
      data: userInfo
    }
  }
}