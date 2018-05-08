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
          crowdInfoExists: false

      };
  }

  componentDidMount() {
    this.getCrowdTotal()
      .then(res => this.setState({ crowdtotal : res.total, crowdInfoExists: true }))
      .catch(err => this.setState({ crowdInfoExists : false }));
    this.getCrowdFrequencies()
      .then(res => this.setState({ freqdata: res.data, frequnits: res.units, crowdInfoExists : true}))
      .catch(err => this.setState({ crowdInfoExists : false }));
  }

  getCrowdTotal = async () => {
    const filenames = /job/ + this.state.jobID + '/total.json';
    const response = await fetch(filenames);
    if (response.status !== 200) throw Error("no crowd");

    const body = response.json();
    return body;
  };

  getCrowdFrequencies = async () => {
    const filenames = /job/ + this.state.jobID + '/frequencies.json';
    const response = await fetch(filenames);
    if (response.status !== 200) throw Error("no freq");

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
      content = <div>
          No crowd info at this time.
      </div>;
    }

    return(
      <div>
        { content }
      </div>
    );
  }
}

export default CrowdInfo;
