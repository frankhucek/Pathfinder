import React, { Component } from 'react';
import Image from 'react-image-resizer';
import project from '../data/out/project.bmp';

class Projection extends Component {
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
                    src={project}
                    height={ this.state.height }
                    width={ this.state.width }
              /></div>
          </div>
      )
  }
}

export default Projection;
