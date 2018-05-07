import React, { Component } from 'react';

class NavBar extends Component {
  constructor(props) {
    super(props);
    this.state = {
        jobID: props.jobID,
        response: ''
    }
  }

  render() {
      return(
          <div className="navbar">
            <div className="navbar-job-id">
                <h3>Job ID: {this.state.jobID}</h3>
            </div>
            <div className="navbar-switch-job-button">
                <button className="general-button" onClick="switch-job-button">
                    Switch Jobs
                </button>
            </div>
          </div>
      )
  }
}

export default NavBar;
