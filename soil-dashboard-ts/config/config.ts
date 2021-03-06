import { IConfig, IPlugin } from "umi-types";
import defaultSettings from "./defaultSettings"; // https://umijs.org/config/

import slash from "slash2";
import webpackPlugin from "./plugin.config";
const { pwa, primaryColor } = defaultSettings; // preview.pro.ant.design only do not use in your production ;
// preview.pro.ant.design 专用环境变量，请不要在你的项目中使用它。

const { SOIL_ONLY_DO_NOT_USE_IN_YOUR_PRODUCTION } = process.env;
const isAntDesignProPreview =
  SOIL_ONLY_DO_NOT_USE_IN_YOUR_PRODUCTION === "site";
const plugins: IPlugin[] = [
  [
    "umi-plugin-react",
    {
      antd: true,
      dva: {
        hmr: true
      },
      locale: {
        // default false
        enable: true,
        // default zh-CN
        default: "zh-CN",
        // default true, when it is true, will use `navigator.language` overwrite default
        baseNavigator: true
      },
      dynamicImport: {
        loadingComponent: "./components/PageLoading/index",
        webpackChunkName: true,
        level: 3
      },
      pwa: pwa
        ? {
            workboxPluginMode: "InjectManifest",
            workboxOptions: {
              importWorkboxFrom: "local"
            }
          }
        : false // default close dll, because issue https://github.com/ant-design/ant-design-pro/issues/4665
      // dll features https://webpack.js.org/plugins/dll-plugin/
      // dll: {
      //   include: ['dva', 'dva/router', 'dva/saga', 'dva/fetch'],
      //   exclude: ['@babel/runtime', 'netlify-lambda'],
      // },
    }
  ],
  [
    "umi-plugin-pro-block",
    {
      moveMock: false,
      moveService: false,
      modifyRequest: true,
      autoAddMenu: true
    }
  ]
]; // 针对 preview.pro.ant.design 的 GA 统计代码

if (isAntDesignProPreview) {
  plugins.push([
    "umi-plugin-ga",
    {
      code: "UA-72788897-6"
    }
  ]);
  plugins.push([
    "umi-plugin-pro",
    {
      serverUrl: "https://ant-design-pro.netlify.com"
    }
  ]);
}

export default {
  plugins,
  proxy: {
    "/api": {
      target: "http://localhost:92",
      changeOrigin: true,
      pathRewrite: { "^/api": "" }
    }
  },
  block: {
    defaultGitUrl: "https://github.com/ant-design/pro-blocks"
  },
  hash: true,
  targets: {
    ie: 11
  },
  devtool: isAntDesignProPreview ? "source-map" : false,
  // umi routes: https://umijs.org/zh/guide/router.html
  routes: [
    {
      path: "/user",
      component: "../layouts/UserLayout",
      routes: [
        {
          path: "/user",
          redirect: "/user/login"
        },
        {
          path: "/user/login",
          name: "login",
          component: "./user/login"
        }
      ]
    },
    {
      path: "/",
      component: "../layouts/BasicLayout",
      Routes: ["src/pages/Authorized"],
      routes: [
        // dashboard
        {
          path: "/",
          redirect: "/dashboard/analysis",
          authority: ["admin", "user"]
        },
        {
          path: "/dashboard",
          name: "dashboard",
          icon: "dashboard",
          routes: [
            {
              path: "/dashboard/analysis",
              name: "analysis",
              component: "./dashboard/analysis"
            }
          ]
        },
        // forms
        {
          path: "/form",
          icon: "form",
          name: "form",
          authority: ["admin"],
          routes: [
            {
              path: "form/basic-form",
              name: "basic-form",
              component: "./form/basic/form"
            }
          ]
        },
        // account
        {
          name: "account",
          icon: "user",
          path: "account",
          routes: [
            {
              name: "center",
              path: "/account/center",
              component: "./account/center"
            },
            {
              name: "settings",
              path: "/account/settings",
              component: "./account/settings"
            }
          ]
        },
        {
          component: "./404"
        }
      ]
    },
    {
      component: "./404"
    }
  ],
  // Theme for antd: https://ant.design/docs/react/customize-theme-cn
  theme: {
    "primary-color": primaryColor
  },
  define: {
    SOIL_ONLY_DO_NOT_USE_IN_YOUR_PRODUCTION:
      SOIL_ONLY_DO_NOT_USE_IN_YOUR_PRODUCTION || "" // preview.pro.ant.design only do not use in your production ; preview.pro.ant.design 专用环境变量，请不要在你的项目中使用它。
  },
  ignoreMomentLocale: true,
  lessLoaderOptions: {
    javascriptEnabled: true
  },
  disableRedirectHoist: true,
  cssLoaderOptions: {
    modules: true,
    getLocalIdent: (
      context: {
        resourcePath: string;
      },
      _: string,
      localName: string
    ) => {
      if (
        context.resourcePath.includes("node_modules") ||
        context.resourcePath.includes("ant.design.pro.less") ||
        context.resourcePath.includes("global.less")
      ) {
        return localName;
      }

      const match = context.resourcePath.match(/src(.*)/);

      if (match && match[1]) {
        const antdProPath = match[1].replace(".less", "");
        const arr = slash(antdProPath)
          .split("/")
          .map((a: string) => a.replace(/([A-Z])/g, "-$1"))
          .map((a: string) => a.toLowerCase());
        return `antd-pro${arr.join("-")}-${localName}`.replace(/--/g, "-");
      }

      return localName;
    }
  },
  manifest: {
    basePath: "/"
  },
  chainWebpack: webpackPlugin
  /*
  proxy: {
    '/server/api/': {
      target: 'https://preview.pro.ant.design/',
      changeOrigin: true,
      pathRewrite: { '^/server': '' },
    },
  },
  */
} as IConfig;
