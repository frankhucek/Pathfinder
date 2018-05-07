import React, { Component } from 'react';
import Image from 'react-image-resizer';
import Whitespace from './Whitespace.js';
import overlay from '../data/out/overlay.bmp';

class AnalyzedInfo extends Component {
  constructor(props) {
      super(props);

      this.state = {
          height: props.height,
          width: props.width,
          retailmap: props.retailmap
      };
  }

  render() {
      return(
          <div className="image-display">
            <Image
                  src={overlay}
                  height={ this.state.height }
                  width={ this.state.width }
            />
          </div>
      )
  }
}

export default AnalyzedInfo;
