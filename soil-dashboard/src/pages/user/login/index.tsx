import React from 'react';
import { useHistory } from 'react-router-dom'
import { Form, Input, Button, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { UserInfo } from '@/store/model/user-info'
import request from '@/utils/request';
import userStore from '@/store/user';

import DefaultSettings from '@/config/defaultSettings';
import styles from './index.less';
import service from './service';

const Login: React.FC = () => {
  const history = useHistory();
  const onFinish = async (values) => {
    const data = await service.login(values);
    const token = data.token;
    request.setHeader({ Authorization: token });
    userStore.setToken(token);
    const userInfoData = await service.userInfo(token);
    userStore.setUserInfo(userInfoData);
    history.replace('/dashboard');
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginName}>
        <div className={styles.loginNameZh}>{DefaultSettings.chineseName}</div>
        <div className={styles.loginNameEn}>{DefaultSettings.englishName}</div>
      </div>
      <Form
        name="normal_login"
        className={styles.loginForm}
        initialValues={{ remember: true }}
        onFinish={onFinish}
      >
        <Form.Item
          name="username"
          rules={[{ required: true, message: '请输入用户名!' }]}
        >
          <Input className={styles.siteFormItemInput} prefix={<UserOutlined className={styles.siteFormItemIcon} />} placeholder="用户名" />
        </Form.Item>
        <Form.Item
          name="password"
          rules={[{ required: true, message: '请输入密码!' }]}
        >
          <Input
            className={styles.siteFormItemInput}
            prefix={<LockOutlined className={styles.siteFormItemIcon} />}
            type="password"
            placeholder="密码"
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" className={styles.loginFromButton}>
            登录
          </Button>
        </Form.Item>

        <Form.Item className={styles.topLine}>
          {/* <Form.Item name="remember" valuePropName="checked" noStyle>
            <Checkbox>记住我</Checkbox>
          </Form.Item> */}

          <a className={styles.loginFromForgot} href="">
            忘记密码 ?
          </a>
        </Form.Item>
      </Form>
    </div>
  )
}

export default Login;