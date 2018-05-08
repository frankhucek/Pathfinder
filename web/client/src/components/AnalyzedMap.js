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
        .then(res => this.setState({ heatmap : res }));
    }

    getHeatmap = async () => {
      const file = '/job/' + this.state.jobID + '/heatmap/';
      const response = await fetch(file);

      return response;
    };

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
