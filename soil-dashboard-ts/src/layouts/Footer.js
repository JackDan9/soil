import React, { Fragment } from "react";
import { Layout, Icon } from "antd";
import GlobalFooter from "@/components/GlobalFooter";

const { Footer } = Layout;

const FooterView = () => (
  <Footer style={{ padding: 0 }}>
    <GlobalFooter
      links={[
        {
          key: "Soil Home",
          title: "Soil Home",
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
