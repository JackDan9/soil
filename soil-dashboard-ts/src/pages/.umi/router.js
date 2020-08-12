import React from "react";
import {
  Router as DefaultRouter,
  Route,
  Switch,
  StaticRouter
} from "react-router-dom";
import dynamic from "umi/dynamic";
import renderRoutes from "umi/lib/renderRoutes";
import history from "@@/history";
import RendererWrapper0 from "/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/pages/.umi/LocaleWrapper.jsx";
import _dvaDynamic from "dva/dynamic";

const Router = require("dva/router").routerRedux.ConnectedRouter;

const routes = [
  {
    path: "/user",
    component: __IS_BROWSER
      ? _dvaDynamic({
          component: () =>
            import(
              /* webpackChunkName: "layouts__UserLayout" */ "../../layouts/UserLayout"
            ),
          LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
            .default
        })
      : require("../../layouts/UserLayout").default,
    routes: [
      {
        path: "/user",
        redirect: "/user/login",
        exact: true
      },
      {
        path: "/user/login",
        name: "login",
        component: __IS_BROWSER
          ? _dvaDynamic({
              app: require("@tmp/dva").getApp(),
              models: () => [
                import(
                  /* webpackChunkName: 'p__user__login__model.ts' */ "/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/pages/user/login/model.ts"
                ).then(m => {
                  return { namespace: "model", ...m.default };
                })
              ],
              component: () =>
                import(
                  /* webpackChunkName: "p__user__login" */ "../user/login"
                ),
              LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
                .default
            })
          : require("../user/login").default,
        exact: true
      },
      {
        component: () =>
          React.createElement(
            require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/node_modules/_umi-build-dev@1.18.5@umi-build-dev/lib/plugins/404/NotFound.js")
              .default,
            { pagesPath: "src/pages", hasRoutesInConfig: true }
          )
      }
    ]
  },
  {
    path: "/",
    component: __IS_BROWSER
      ? _dvaDynamic({
          component: () =>
            import(
              /* webpackChunkName: "layouts__BasicLayout" */ "../../layouts/BasicLayout"
            ),
          LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
            .default
        })
      : require("../../layouts/BasicLayout").default,
    Routes: [require("../Authorized").default],
    routes: [
      {
        path: "/",
        redirect: "/dashboard/analysis",
        authority: ["admin", "user"],
        exact: true
      },
      {
        path: "/dashboard",
        name: "dashboard",
        icon: "dashboard",
        routes: [
          {
            path: "/dashboard/analysis",
            name: "analysis",
            component: __IS_BROWSER
              ? _dvaDynamic({
                  app: require("@tmp/dva").getApp(),
                  models: () => [
                    import(
                      /* webpackChunkName: 'p__dashboard__analysis__model.tsx' */ "/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/pages/dashboard/analysis/model.tsx"
                    ).then(m => {
                      return { namespace: "model", ...m.default };
                    })
                  ],
                  component: () =>
                    import(
                      /* webpackChunkName: "p__dashboard__analysis" */ "../dashboard/analysis"
                    ),
                  LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
                    .default
                })
              : require("../dashboard/analysis").default,
            exact: true
          },
          {
            component: () =>
              React.createElement(
                require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/node_modules/_umi-build-dev@1.18.5@umi-build-dev/lib/plugins/404/NotFound.js")
                  .default,
                { pagesPath: "src/pages", hasRoutesInConfig: true }
              )
          }
        ]
      },
      {
        path: "/form",
        icon: "form",
        name: "form",
        authority: ["admin"],
        routes: [
          {
            path: "/form/form/basic-form",
            name: "basic-form",
            component: __IS_BROWSER
              ? _dvaDynamic({
                  app: require("@tmp/dva").getApp(),
                  models: () => [
                    import(
                      /* webpackChunkName: 'p__form__basic__form__model.ts' */ "/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/pages/form/basic/form/model.ts"
                    ).then(m => {
                      return { namespace: "model", ...m.default };
                    })
                  ],
                  component: () =>
                    import(
                      /* webpackChunkName: "p__form__basic__form" */ "../form/basic/form"
                    ),
                  LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
                    .default
                })
              : require("../form/basic/form").default,
            exact: true
          },
          {
            component: () =>
              React.createElement(
                require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/node_modules/_umi-build-dev@1.18.5@umi-build-dev/lib/plugins/404/NotFound.js")
                  .default,
                { pagesPath: "src/pages", hasRoutesInConfig: true }
              )
          }
        ]
      },
      {
        name: "account",
        icon: "user",
        path: "/account",
        routes: [
          {
            name: "center",
            path: "/account/center",
            component: __IS_BROWSER
              ? _dvaDynamic({
                  app: require("@tmp/dva").getApp(),
                  models: () => [
                    import(
                      /* webpackChunkName: 'p__account__center__model.ts' */ "/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/pages/account/center/model.ts"
                    ).then(m => {
                      return { namespace: "model", ...m.default };
                    })
                  ],
                  component: () =>
                    import(
                      /* webpackChunkName: "p__account__center" */ "../account/center"
                    ),
                  LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
                    .default
                })
              : require("../account/center").default,
            exact: true
          },
          {
            name: "settings",
            path: "/account/settings",
            component: __IS_BROWSER
              ? _dvaDynamic({
                  app: require("@tmp/dva").getApp(),
                  models: () => [
                    import(
                      /* webpackChunkName: 'p__account__settings__model.ts' */ "/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/pages/account/settings/model.ts"
                    ).then(m => {
                      return { namespace: "model", ...m.default };
                    })
                  ],
                  component: () =>
                    import(
                      /* webpackChunkName: "p__account__settings" */ "../account/settings"
                    ),
                  LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
                    .default
                })
              : require("../account/settings").default,
            exact: true
          },
          {
            component: () =>
              React.createElement(
                require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/node_modules/_umi-build-dev@1.18.5@umi-build-dev/lib/plugins/404/NotFound.js")
                  .default,
                { pagesPath: "src/pages", hasRoutesInConfig: true }
              )
          }
        ]
      },
      {
        component: __IS_BROWSER
          ? _dvaDynamic({
              component: () =>
                import(/* webpackChunkName: "p__404" */ "../404"),
              LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
                .default
            })
          : require("../404").default,
        exact: true
      },
      {
        component: () =>
          React.createElement(
            require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/node_modules/_umi-build-dev@1.18.5@umi-build-dev/lib/plugins/404/NotFound.js")
              .default,
            { pagesPath: "src/pages", hasRoutesInConfig: true }
          )
      }
    ]
  },
  {
    component: __IS_BROWSER
      ? _dvaDynamic({
          component: () => import(/* webpackChunkName: "p__404" */ "../404"),
          LoadingComponent: require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/src/components/PageLoading/index")
            .default
        })
      : require("../404").default,
    exact: true
  },
  {
    component: () =>
      React.createElement(
        require("/Users/jackdan/Downloads/workspace/soil/soil-dashboard-ts/node_modules/_umi-build-dev@1.18.5@umi-build-dev/lib/plugins/404/NotFound.js")
          .default,
        { pagesPath: "src/pages", hasRoutesInConfig: true }
      )
  }
];
window.g_routes = routes;
const plugins = require("umi/_runtimePlugin");
plugins.applyForEach("patchRoutes", { initialValue: routes });

export { routes };

export default class RouterWrapper extends React.Component {
  unListen() {}

  constructor(props) {
    super(props);

    // route change handler
    function routeChangeHandler(location, action) {
      plugins.applyForEach("onRouteChange", {
        initialValue: {
          routes,
          location,
          action
        }
      });
    }
    this.unListen = history.listen(routeChangeHandler);
    // dva 中 history.listen 会初始执行一次
    // 这里排除掉 dva 的场景，可以避免 onRouteChange 在启用 dva 后的初始加载时被多执行一次
    const isDva =
      history.listen
        .toString()
        .indexOf("callback(history.location, history.action)") > -1;
    if (!isDva) {
      routeChangeHandler(history.location);
    }
  }

  componentWillUnmount() {
    this.unListen();
  }

  render() {
    const props = this.props || {};
    return (
      <RendererWrapper0>
        <Router history={history}>{renderRoutes(routes, props)}</Router>
      </RendererWrapper0>
    );
  }
}
