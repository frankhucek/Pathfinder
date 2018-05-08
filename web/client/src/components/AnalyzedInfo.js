import React, { Component } from 'react';
import Image from 'react-image-resizer';

class AnalyzedInfo extends Component {
  constructor(props) {
      super(props);

      this.state = {
          jobID: props.jobID,
          height: props.height,
          width: props.width,
          overlay: '/job/' + props.jobID + '/overlay.bmp'
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
