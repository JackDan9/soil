import React, { PureComponent } from 'react';

import { GridContent } from '@ant-design/pro-layout';


class Network extends PureComponent<{}> {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <GridContent>
        <div>Network</div>
      </GridContent>
    )
  }
}

export default Network;