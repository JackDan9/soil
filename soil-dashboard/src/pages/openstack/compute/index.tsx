import React, { PureComponent } from 'react';

import { GridContent } from '@ant-design/pro-layout';


class Compute extends PureComponent<{}> {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <GridContent>
        <div>Compute</div>
      </GridContent>
    )
  }
}

export default Compute;