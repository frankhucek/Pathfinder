import React, { Component } from 'react';

class CrowdInfo extends Component {
  constructor(props) {
      super(props);

      this.state = {
          jobID: props.jobID,
          height: props.height,
          width: props.width,
          freqdata: '',
          frequnits: '',
          crowdtotal: '',

      };
  }

  componentDidMount() {
    this.getCrowdTotal()
      .then(res => this.setState({ crowdtotal : res.total }));
    this.getCrowdFrequencies()
      .then(res => this.setState({ freqdata: res.data, frequnits: res.units}));
  }

  getCrowdTotal = async () => {
    const filenames = /job/ + this.state.jobID + '/crowd/total.json';
    console.log(filenames);
    const response = await fetch(filenames);
    const body = response.json();

    return body;
  };

  getCrowdFrequencies = async () => {
    const filenames = /job/ + this.state.jobID + '/crowd/freq.json';
    console.log(filenames);
    const response = await fetch(filenames);
    const body = response.json();

    return body;
  };
  render() {
    let content = null;
    try {
      content = <div className="image-display">
        <p>Units: {this.state.frequnits}</p>
        Total: {this.state.crowdtotal}
        <ul>
        {
          this.state.freqdata.map(function(period){
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
