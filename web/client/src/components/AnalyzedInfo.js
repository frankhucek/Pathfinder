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
          overlay: ''
      };
  }

  componentDidMount() {
    this.getHeatmap()
      .then(res => this.setState({ overlay: res }))
      .catch(err => { console.log("eror"); console.log(err);});
    console.log("mounted");
  }

  getHeatmap = async () => {
    const overlay_get = /job/ + this.state.jobID + '/overlay/';
    const response = await fetch(overlay_get);

    return overlay_get;
  };

  render() {
      var overlay = 'http://localhost:4000' + this.state.overlay;
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
