import React, { Component } from 'react';
import Whitespace from './Whitespace.js';
import retailmap from '../data/heatmap.png';

class AnalyzedInfo extends React.Component {
  constructor(props) {
      super(props);

      this.state = {
          traffic: 0,
          retailmap: null
      };
  }

  render() {
      let content = null;
      content = <img src={retailmap} />;
      content += <Whitespace />;

      return(
          <div class="analyzed-info">
              { content }
          </div>
      )
  }
}

export default AnalyzedInfo;
