/**
 * Ant Design Pro v4 use `@ant-design/pro-layout` to handle Layout.
 * You can view component api by:
 * https://github.com/ant-design/ant-design-pro-layout
 */

import React, { Fragment } from "react";
import { Layout, Icon } from "antd";
import GlobalFooter from "@/components/GlobalFooter";

const { Footer } = Layout;

const FooterView = () => (
  <Footer style={{ padding: 0 }}>
    <GlobalFooter
      links={[
        {
          key: "Soil",
          title: "Soil",
          href: "/",
          blankTarget: true
        },
        {
          key: "github",
          title: <Icon type="github" />,
          href: "https://github.com/JackDan",
          blankTarget: true
        },
        {
          key: "Soil",
          title: "Soil",
          href: "/",
          blankTarget: true
        }
      ]}
      copyright={
        <Fragment>
          Copyright <Icon type="copyright" /> 2020 JackDan Open Source Community
        </Fragment>
      }
    />
  </Footer>
);

export default FooterView;
