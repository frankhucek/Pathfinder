import React, { Component } from 'react';
import Image from 'react-image-resizer';
import job_image_0 from '../data/out/heatmap.bmp';

class AnalyzedMap extends Component {
    constructor(props) {
        super(props);

        this.state = {
            height: props.height,
            width: props.width
        }
    }

  render() {
      return (
          <div className="image-display">
              <div><Image
                    src={job_image_0}
                    height={ this.state.height }
                    width={ this.state.width }
              /></div>
          </div>
      )
  }
}

export default AnalyzedMap;
