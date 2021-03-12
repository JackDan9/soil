import React, { PureComponent } from 'react';

import { GridContent } from '@ant-design/pro-layout';


class VCenter extends PureComponent<{}> {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <GridContent>
        <div>VCenter</div>
      </GridContent>
    )
  }
}

export default VCenter;