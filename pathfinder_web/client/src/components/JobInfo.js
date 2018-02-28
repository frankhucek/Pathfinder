import React, { Component } from 'react';
import NavBar from './NavBar.js';
import Images from './Images.js';
import AnalyzedMap from './AnalyzedMap.js';
import AnalyzedInfo from './AnalyzedInfo.js';

class JobInfo extends Component {
    render() {
        return (
            <div className="job-info">
                <NavBar/>
                <Images/>
                <AnalyzedMap mapType="heatmap"/>
                <AnalyzedMap mapType="blueprint"/>
                <AnalyzedInfo/>
            </div>
        )
    }
}

export default JobInfo;
