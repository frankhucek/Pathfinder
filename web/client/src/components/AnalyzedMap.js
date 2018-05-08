import React, { Component } from 'react';
import Image from 'react-image-resizer';

class AnalyzedMap extends Component {
    constructor(props) {
        super(props);

        this.state = {
            jobID: props.jobID,
            heatmap: '/job/' + props.jobID + '/heatmap.bmp',
            height: props.height,
            width: props.width
        }
    }

  render() {
      return (
          <div className="image-display">
              <div><Image
                    src={this.state.heatmap}
                    height={ this.state.height }
                    width={ this.state.width }
              /></div>
          </div>
      )
  }
}

export default AnalyzedMap;
