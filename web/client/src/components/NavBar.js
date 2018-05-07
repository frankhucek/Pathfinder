import React, { Component } from 'react';
import { Redirect } from 'react-router';

class NavBar extends Component {
  constructor(props) {
    super(props);
    this.state = {
        jobID: props.jobID,
        fireRedirect: false
    }
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
  }

  handleSubmit(event) {
    event.preventDefault();
    this.setState({ fireRedirect: true })
  }

  render() {
      return(
          <div className="navbar">
            <div className="navbar-job-id">
                <h3>Job ID: {this.state.jobID}</h3>
            </div>
            <div className="navbar-switch-job-button">
              <form onSubmit={this.handleSubmit}>
                <button type="submit" className="general-button" onClick="switch-job-button">
                    Switch Jobs
                </button>
              </form>
              {this.state.fireRedirect && (
                <Redirect to={{
                    pathname: '/'
                  }}/>
              )}

            </div>
          </div>
      )
  }
}

export default NavBar;
