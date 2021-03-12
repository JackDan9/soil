// VMware || 管理VMware资源
import { lazy } from 'react';
import CommonRoute from '../CommonRoute';

const VCenter = lazy(
  () => import(/* wepackChunkName: "vcenter" */ '@/pages/vmware/vcenter')
)

const Overview = lazy(
  () => import(/* wepackChunkName: "overview" */ '@/pages/vmware/overview')
)

const Compute = lazy(
  () => import(/* wepackChunkName: "compute" */ '@/pages/vmware/compute')
)

const Storage = lazy(
  () => import(/* webpackChunkName: "storage" */ '@/pages/vmware/storage')
)

const Network = lazy(
  () => import(/* webpackChunkName: "network" */ '@/pages/vmware/network')
)


const route: CommonRoute = {
  name: 'vmware',
  title: 'VMware管理',
  icon: 'vmware',
  path: '/vmware',
  children: [
    {
      name: 'vcenter',
      title: '管理资源',
      path: '/vmware/vcenter',
      exact: true,
      component: VCenter
    },
    {
      name: 'overview',
      title: '概览',
      path: '/vmware/overview',
      exact: true,
      component: Overview
    },
    {
      name: 'compute',
      title: '计算资源',
      path: '/vmware/compute',
      exact: true,
      component: Compute
    },
    {
      name: 'storage',
      title: '存储资源',
      path: '/vmware/storage',
      exact: true,
      component: Storage
    },
    {
      name: 'network',
      title: '网络资源',
      path: '/vmware/network',
      exact: true,
      component: Network
    },

  ]
}

export default route;