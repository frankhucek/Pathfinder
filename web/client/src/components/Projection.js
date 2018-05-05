import React, { Component } from 'react';
import Image from 'react-image-resizer';

class Projection extends Component {
    constructor(props) {
        super(props);

        this.state = {
            height: props.height,
            width: props.width
        }
    }

  render() {
    let content = null;
    try {
      var project = require('../data/out/project.bmp');
      content = <div className="image-display">
          <div><Image
                src={project}
                height={ this.state.height }
                width={ this.state.width }
          /></div>
      </div>;
    }
    catch (e) {
      content = null;
    }

      return (
        <div>
          { content }
        </div>
      )
  }
}

export default Projection;
