import React, { Component } from 'react';
import NavBar from './NavBar.js';
import JobInfoCard from './JobInfoCard.js'
import ErrorPage from './ErrorPage.js'

class JobPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      jobID: this.props.location.state.jobID,
      jobExists: false
    }
  }

  componentDidMount() {
    this.checkJobExists()
      .then(res => this.setState({ jobExists : true }))
      .catch(err => this.setState({ jobExists : false }))
  }

  checkJobExists = async () => {
    const filenames = /job/ + this.state.jobID + '/allimages/';
    const response = await fetch(filenames);
    const body = response.json();

    if (response.status !== 200) throw Error(body.message);

    return body;
  };

  render() {
      if (!this.state.jobExists) {
          return (
            <div className="job-info-page">
              <NavBar jobID={this.state.jobID}/>
              <ErrorPage />
            </div>
          );
      }

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
            <JobInfoCard cardType="retail" header="potential retail places"
              jobID={this.state.jobID}/>
        </div>
      )
  }
}

export default JobPage;
