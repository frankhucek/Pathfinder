import React, { Component } from 'react';
import NavBar from './NavBar.js';
import JobInfoCard from './JobInfoCard.js'

class JobPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      jobID: this.props.location.state.jobID
    }
  }

  render() {
      return (
        <div className="job-info-page">
            <NavBar jobID={this.state.jobID}/>
            <JobInfoCard cardType="images" header="your images"
                          jobID={this.state.jobID}/>
            <JobInfoCard cardType="heatmap" header="analyzed heatmap"
                          jobID={this.state.jobID}/>
            <JobInfoCard cardType="overlay" header="overlayed heatmap"
                          jobID={this.state.jobID}/>
            <JobInfoCard cardType="project" header="projection"
              jobID={this.state.jobID}/>
            <JobInfoCard cardType="crowd" header="crowd info"
              jobID={this.state.jobID}/>
        </div>
      )
  }
}

export default JobPage;
