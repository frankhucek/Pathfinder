import React, { Component } from 'react';
import NavBar from './NavBar.js';
import JobInfoCard from './JobInfoCard.js'

class JobPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      jobID: this.props.location.state.jobID,
      images: props.images,
      heatmap: props.heatmap,
      retailmap: props.retailmap
    }
  }

    getDependencies() {
      var frequencies;
      var total;
      var project;
      try {
        frequencies = require('../data/out/frequencies.json');
      }
      catch (e) {
        frequencies = null;
      }
      try {
        total = require('../data/out/total.json');
      }
      catch (e) {
        total = null;
      }
      try {
        project = require('../data/out/project.bmp');
      }
      catch (e) {
        project = null;
      }
      return [frequencies, total, project]
    }

    render() {
        var values = this.getDependencies()
        let crowd_data = values.frequencies != null && values.total != null;
        let project_data = values.project != null;

        return (
            <div className="job-info-page">
                <NavBar/>
                <JobInfoCard cardType="images" header="your images"
                              images={this.state.images}/>
                <JobInfoCard cardType="heatmap" header="analyzed heatmap"
                              heatmap={this.state.heatmap}/>
                <JobInfoCard cardType="overlay" header="overlayed heatmap"
                              retailmap={this.state.retailmap}/>
                {project_data && <JobInfoCard cardType="project" header="projected heatmap" />}
                {crowd_data && <JobInfoCard cardType="crowd" header="crowd usage" />}
            </div>
        )
    }
}

export default JobPage;
