import React, { Component } from 'react';
import NavBar from './NavBar.js';
import JobInfoCard from './JobInfoCard.js'

class JobPage extends Component {
    render() {
        return (
            <div className="job-info-page">
                <NavBar/>
                <JobInfoCard />
            </div>
        )
    }
}

export default JobPage;
