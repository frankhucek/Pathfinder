import React, { Component } from 'react';
import NavBar from './NavBar.js';
import JobInfoCard from './JobInfoCard.js'

class JobPage extends Component {
    render() {
        return (
            <div className="job-info-page">
                <NavBar/>
                <JobInfoCard cardType="images" header="your images" />
                <JobInfoCard cardType="heatmap" header="analyzed heatmap" />
                <JobInfoCard cardType="overlay" header="overlayed heatmap" />
            </div>
        )
    }
}

export default JobPage;
