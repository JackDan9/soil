// 登录
// import $request from '@/utils/request';

const login = async (params: { username: string; password: string; }) => {
  const res = await $request.post('/user/login', params)
  return res
}

const userInfo = async (token) => {
  const res = await $request.get('/user/userInfo?token=' + token)
  return res
}

export default {
  login,
  userInfo
}