import React, { PureComponent } from 'react';

import { GridContent } from '@ant-design/pro-layout';


class Management extends PureComponent<{}> {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <GridContent>
        <div>Management</div>
      </GridContent>
    )
  }
}

export default Management;