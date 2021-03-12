import React, { PureComponent } from 'react';

import { GridContent } from '@ant-design/pro-layout';


class Overview extends PureComponent<{}> {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <GridContent>
        <div>Overview</div>
      </GridContent>
    )
  }
}

export default Overview;