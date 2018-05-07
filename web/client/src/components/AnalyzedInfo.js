import React, { Component } from 'react';
import Image from 'react-image-resizer';
import Whitespace from './Whitespace.js';

class AnalyzedInfo extends Component {
  constructor(props) {
      super(props);

      this.state = {
          jobID: props.jobID,
          height: props.height,
          width: props.width,
          overlay: 'http://localhost:4000/job/' + props.jobID + '/overlay/'
      };
  }

  render() {
      return(
          <div className="image-display">
            <Image
                  src={this.state.overlay}
                  height={ this.state.height }
                  width={ this.state.width }
            />
          </div>
      )
  }
}

export default AnalyzedInfo;
