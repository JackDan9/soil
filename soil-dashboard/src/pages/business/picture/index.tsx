import React, { PureComponent } from 'react';

import { GridContent } from '@ant-design/pro-layout';

import style from './index.less';


class Picture extends PureComponent<{}> {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <GridContent>
        <div>Picture</div>
      </GridContent>
    )
  }
}

export default Picture;