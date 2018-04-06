import React, { Component } from 'react';
import Images from './Images.js'
import Whitespace from './Whitespace.js'

class JobInfoCard extends Component {
    render() {
        return(
            <div className="job-info-card">
                <Whitespace header="your images"/>
                <Images />
            </div>
        )
    }
}

export default JobInfoCard;
