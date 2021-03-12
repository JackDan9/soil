import React, { PureComponent } from 'react';

import { GridContent } from '@ant-design/pro-layout';


class Storage extends PureComponent<{}> {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <GridContent>
        <div>Storage</div>
      </GridContent>
    )
  }
}

export default Storage;