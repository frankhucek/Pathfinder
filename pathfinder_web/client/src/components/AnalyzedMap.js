import React, { Component } from 'react';
import heatmap from '../data/heatmap.png';
import blueprint from '../data/3.jpg'

class AnalyzedMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
        mapType: this.props.mapType
    }
  }

  render() {
      let content = null;
      if (this.props.mapType == "heatmap") {
          content = <img src={heatmap} />;
          content += <Whitespace />;
      }
      else {
          content = <Whitespace />;
          content += <img src={blueprint} />;
      }

      return (
          <div>
              <div className={this.props.mapType}>
                { content }
              </div>

          </div>
      )
  }
}

export default AnalyzedMap;
