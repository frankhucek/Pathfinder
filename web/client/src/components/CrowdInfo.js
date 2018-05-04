import React, { Component } from 'react';
import Image from 'react-image-resizer';
import Whitespace from './Whitespace.js';

import frequencies from '../data/out/frequencies.json';
import total from '../data/out/total.json'

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
    return(
        <div className="image-display">
          <p>Units: {frequencies.units}</p>
          Total: {total.total}
          <ul>
          {
            frequencies.data.map(function(period){
              return <li>{period.start} to {period.end}: {period.rate}</li>;
            })
          }
          </ul>
        </div>
    );
  }
}

export default CrowdInfo;
