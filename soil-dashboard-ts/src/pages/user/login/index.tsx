import { Alert, Checkbox } from "antd";
import { FormattedMessage, formatMessage } from "umi-plugin-react/locale";
import React, { Component } from "react";

import { CheckboxChangeEvent } from "antd/es/checkbox";
import { Dispatch } from "redux";
import { FormComponentProps } from "antd/es/form";
import { connect } from "dva";
import { StateType } from "./model";
import LoginComponents from "./components/Login";
import styles from "./style.less";

const { Tab, UserName, Password, Submit } = LoginComponents;

interface LoginProps {
  dispatch: Dispatch<any>;
  userLogin: StateType;
  submitting: boolean;
}
interface LoginState {
  type: string;
  autoLogin: boolean;
}
export interface FromDataType {
  userName: string;
  password: string;
  mobile: string;
  captcha: string;
}

@connect(
  ({
    userLogin,
    loading
  }: {
    userLogin: StateType;
    loading: {
      effects: {
        [key: string]: string;
      };
    };
  }) => ({
    userLogin,
    submitting: loading.effects["userLogin/login"]
  })
)
class Login extends Component<LoginProps, LoginState> {
  loginForm: any = undefined;

  state: LoginState = {
    type: "account",
    autoLogin: true
  };

  changeAutoLogin = (e: CheckboxChangeEvent) => {
    this.setState({
      autoLogin: e.target.checked
    });
  };

  handleSubmit = (err: any, values: FromDataType) => {
    const { type } = this.state;
    if (!err) {
      const { dispatch } = this.props;
      dispatch({
        type: "userLogin/login",
        payload: {
          ...values,
          type
        }
      });
    }
  };

  onTabChange = (type: string) => {
    this.setState({ type });
  };

  renderMessage = (content: string) => (
    <Alert
      style={{ marginBottom: 24 }}
      message={content}
      type="error"
      showIcon
    />
  );

  render() {
    const { userLogin, submitting } = this.props;
    const { status, type: loginType } = userLogin;
    const { type, autoLogin } = this.state;
    return (
      <div className={styles.main}>
        <LoginComponents
          defaultActiveKey={type}
          onTabChange={this.onTabChange}
          onSubmit={this.handleSubmit}
          ref={(form: any) => {
            this.loginForm = form;
          }}
        >
          <Tab
            key="account"
            tab={formatMessage({
              id: "user-login.login.tab-login-credentials"
            })}
          >
            {status === "error" &&
              loginType === "account" &&
              !submitting &&
              this.renderMessage(
                formatMessage({
                  id: "user-login.login.message-invalid-credentials"
                })
              )}
            <UserName
              name="username"
              placeholder={`${formatMessage({
                id: "user-login.login.userName"
              })}: admin or user`}
              rules={[
                {
                  required: true,
                  message: formatMessage({ id: "user-login.userName.required" })
                }
              ]}
            />
            <Password
              name="password"
              placeholder={`${formatMessage({
                id: "user-login.login.password"
              })}: passw0rd`}
              rules={[
                {
                  required: true,
                  message: formatMessage({ id: "user-login.password.required" })
                }
              ]}
              onPressEnter={e => {
                e.preventDefault();
                this.loginForm.validateFields(this.handleSubmit);
              }}
            />
          </Tab>
          <div>
            <Checkbox checked={autoLogin} onChange={this.changeAutoLogin}>
              <FormattedMessage id="user-login.login.remember-me" />
            </Checkbox>
            <a style={{ float: "right" }} href="">
              <FormattedMessage id="user-login.login.forgot-password" />
            </a>
          </div>
          <Submit loading={submitting}>
            <FormattedMessage id="user-login.login.login" />
          </Submit>
        </LoginComponents>
      </div>
    );
  }
}

export default Login;
