import React, { Component } from 'react';
import Image from 'react-image-resizer';
import Whitespace from './Whitespace.js';

class CrowdInfo extends Component {
  constructor(props) {
      super(props);

      this.state = {
          height: props.height,
          width: props.width,
          crowd: 0,
          retailmap: null
      };
  }

  render() {
    let content = null;
    try {
      var frequencies = require('../data/out/frequencies.json');
      var total = require('../data/out/total.json');
      content = <div className="image-display">
        <p>Units: {frequencies.units}</p>
        Total: {total.total}
        <ul>
        {
          frequencies.data.map(function(period){
            return <li>{period.start} to {period.end}: {period.rate}</li>;
          })
        }
        </ul>
      </div>;
    }
    catch (e) {
      content = null;
    }

    return(
      <div>
        { content }
      </div>
    );
  }
}

export default CrowdInfo;
