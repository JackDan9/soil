import { DefaultFooter, MenuDataItem, getMenuData, getPageTitle } from '@ant-design/pro-layout';
// import DocumentTitle from 'react-document-title';
import { Helmet } from 'react-helmet';
import Link from 'umi/link';
import React, {Fragment} from 'react';
import { connect } from 'dva';
import { formatMessage } from 'umi-plugin-react/locale';

import GlobalFooter from "@/components/GlobalFooter";
import SelectLang from '@/components/SelectLang';
import { ConnectProps, ConnectState } from '@/models/connect';
import logo from '../assets/logo.svg';
import styles from './UserLayout.less';
import {Icon} from "antd";

export interface UserLayoutProps extends ConnectProps {
  breadcrumbNameMap: { [path: string]: MenuDataItem };
}

const UserLayout: React.SFC<UserLayoutProps> = props => {
  const {
    route = {
      routes: [],
    },
  } = props;
  const { routes = [] } = route;
  const {
    children,
    location = {
      pathname: '',
    },
  } = props;
  const { breadcrumb } = getMenuData(routes);

  const links = [
    {
      key: 'help',
      title: formatMessage({ id: 'layout.user.link.help' }),
      href: '',
    },
    {
      key: 'privacy',
      title: formatMessage({ id: 'layout.user.link.privacy' }),
      href: '',
    },
    {
      key: 'terms',
      title: formatMessage({ id: 'layout.user.link.terms' }),
      href: '',
    },
  ];

  const copyright = (
    <Fragment>
      Copyright <Icon type="copyright" /> 2019 JackDan Open Source Community 
    </Fragment>
  );

  const title = getPageTitle({
    pathname: location.pathname,
    breadcrumb,
    formatMessage,
    ...props,
  });


  return (
    <>
    {/* <DocumentTitle
      title={getPageTitle({
        pathname: location.pathname,
        breadcrumb,
        formatMessage,
        ...props,
      })}
    > */}
      <Helmet>
        <title>{title}</title>
        <meta name="description" content={title} />
      </Helmet>
      <div className={styles.container}>
        <div className={styles.lang}>
          <SelectLang />
        </div>
        <div className={styles.content}>
          <div className={styles.top}>
            <div className={styles.header}>
              <Link to="/">
                <img alt="logo" className={styles.logo} src={logo} />
                <span className={styles.title}>Soil</span>
              </Link>
            </div>
            <div className={styles.desc}>{formatMessage({ id: 'layout.user.description' })}</div>
          </div>
          {children}
        </div>
        <GlobalFooter links={links} copyright={copyright} />
        {/* <DefaultFooter /> */}
      </div>
    {/* </DocumentTitle> */}
    </>
  );
};

export default connect(({ settings }: ConnectState) => ({
  ...settings,
}))(UserLayout);
