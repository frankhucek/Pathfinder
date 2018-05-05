import React, { Component } from 'react';
import NavBar from './NavBar.js';
import JobInfoCard from './JobInfoCard.js'

class JobPage extends Component {
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
                <JobInfoCard cardType="images" header="your images" />
                <JobInfoCard cardType="heatmap" header="analyzed heatmap" />
                <JobInfoCard cardType="overlay" header="overlayed heatmap" />
                {project_data && <JobInfoCard cardType="project" header="projected heatmap" />}
                {crowd_data && <JobInfoCard cardType="crowd" header="crowd usage" />}
            </div>
        )
    }
}

export default JobPage;
