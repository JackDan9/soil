// Openstack || 管理Openstack资源
import { lazy } from 'react';
import CommonRoute from '../CommonRoute';

const Management = lazy(
  () => import(/* wepackChunkName: "management" */ '@/pages/openstack/management')
)

const Overview = lazy(
  () => import(/* wepackChunkName: "overview" */ '@/pages/openstack/overview')
)

const Compute = lazy(
  () => import(/* wepackChunkName: "compute" */ '@/pages/openstack/compute')
)

const Storage = lazy(
  () => import(/* webpackChunkName: "storage" */ '@/pages/openstack/storage')
)

const Network = lazy(
  () => import(/* webpackChunkName: "network" */ '@/pages/openstack/network')
)

const route: CommonRoute = {
  name: 'openstack',
  title: 'Openstack管理',
  icon: 'openstack',
  path: '/openstack',
  children: [
    {
      name: 'management',
      title: '管理资源',
      path: '/openstack/management',
      exact: true,
      component: Management
    },
    {
      name: 'overview',
      title: '概览',
      path: '/openstack/overview',
      exact: true,
      component: Overview
    },
    {
      name: 'compute',
      title: '计算资源',
      path: '/openstack/compute',
      exact: true,
      component: Compute
    },
    {
      name: 'storage',
      title: '存储资源',
      path: '/openstack/storage',
      exact: true,
      component: Storage
    },
    {
      name: 'network',
      title: '网络资源',
      path: '/openstack/network',
      exact: true,
      component: Network
    },

  ]
}

export default route;