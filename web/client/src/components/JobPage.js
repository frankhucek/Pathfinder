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
      //console.log(this.state.jobID);

      return (
        <div className="job-info-page">
            <NavBar jobID={this.state.jobID}/>
            <JobInfoCard cardType="images" header="your images"
                          images={this.state.images}/>
            <JobInfoCard cardType="heatmap" header="analyzed heatmap"
                          jobID={this.state.jobID}/>
            <JobInfoCard cardType="overlay" header="overlayed heatmap"
                          retailmap={this.state.retailmap}/>
            <JobInfoCard cardType="project" header="projected heatmap" />
            <JobInfoCard cardType="crowd" header="crowd usage" />
        </div>
      )
  }
}

export default JobPage;
