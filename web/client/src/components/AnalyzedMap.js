import React, { Component } from 'react';
import Image from 'react-image-resizer';

class AnalyzedMap extends Component {
    constructor(props) {
        super(props);

        this.state = {
            jobID: props.jobID,
            heatmap: '',
            height: props.height,
            width: props.width
        }
    }

    componentDidMount() {
      this.getHeatmap()
        .then(res => this.setState({ heatmap: res }))
        .catch(err => { console.log("eror"); console.log(err);});
      console.log("mounted");
    }

    getHeatmap = async () => {
      const heatmap_get = /job/ + this.state.jobID + '/heatmap/';
      const response = await fetch(heatmap_get);

      return heatmap_get;
    };

  render() {
      var heatmap = 'http://localhost:4000' + this.state.heatmap;
      console.log(this.state.jobID);
      return (
          <div className="image-display">
              <div><Image
                    src={heatmap}
                    height={ this.state.height }
                    width={ this.state.width }
              /></div>
          </div>
      )
  }
}

export default AnalyzedMap;
