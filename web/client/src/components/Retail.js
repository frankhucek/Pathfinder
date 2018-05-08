import React, { Component } from 'react';
import Image from 'react-image-resizer';

class Projection extends Component {
    constructor(props) {
        super(props);

        this.state = {
            height: props.height,
            width: props.width,
            retail: '/job/' + props.jobID + '/retail.jpeg',
        }
    }

  render() {
      return (
        <div>
          <div className="image-display">
              <div><Image
                    src={this.state.retail}
                    height={ this.state.height }
                    width={ this.state.width }
              /></div>
          </div>
        </div>
      )
  }
}

export default Projection;
