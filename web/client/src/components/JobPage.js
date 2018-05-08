import React, { Component } from 'react';
import NavBar from './NavBar.js';
import JobInfoCard from './JobInfoCard.js'
import ErrorPage from './ErrorPage.js'

class JobPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      jobID: this.props.location.state.jobID,
      jobExists: false,
      projectExists: false,
      crowdExists: false,
      retailExists: false
    }
  }

  componentDidMount() {
    this.checkJobExists()
      .then(res => this.setState({ jobExists : true }))
      .catch(err => this.setState({ jobExists : false }))
    this.checkProject()
      .then(res => this.setState({ projectExists : true }))
      .catch(err => this.setState({ projectExists : false }))
    this.checkCrowd()
      .then(res => this.setState({ crowdExists : true }))
      .catch(err => this.setState({ crowdExists : false }))
    this.checkRetail()
      .then(res => this.setState({ retailExists : true }))
      .catch(err => this.setState({ retailExists : false }))
  }

  checkJobExists = async () => {
    const filenames = /job/ + this.state.jobID + '/allimages/';
    const response = await fetch(filenames);
    console.log("job" + response.status);
    if (response.status !== 200) throw Error("no job");

    const body = response.json();
    return body;
  };

  checkProject = async () => {
    const filenames = /job/ + this.state.jobID + '/project.bmp';
    const response = await fetch(filenames);
    console.log("project" + response.status);
    if (response.status !== 200) throw Error("no project");
    return response;
  };

  checkRetail = async () => {
    const filenames = /job/ + this.state.jobID + '/retail.jpeg';
    const response = await fetch(filenames);
    console.log("retail" + response.status);
    if (response.status !== 200) throw Error("no retail");
    return response;
  };

  checkCrowd = async () => {
    const filenames = /job/ + this.state.jobID + '/total.json';
    const response = await fetch(filenames);
    console.log("crowd" + response.status);
    if (response.status !== 200) throw Error("no crowd");
    return response;
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
            { this.state.projectExists &&
              <JobInfoCard cardType="project" header="projection"
              jobID={this.state.jobID}/> }
            { this.state.crowdExists &&
            <JobInfoCard cardType="crowd" header="crowd info"
              jobID={this.state.jobID}/> }
            { this.state.retailExists &&
            <JobInfoCard cardType="retail" header="potential retail places"
              jobID={this.state.jobID}/> }
        </div>
      )
  }
}

export default JobPage;
