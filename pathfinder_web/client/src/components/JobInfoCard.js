import React, { Component } from 'react';
import classnames from 'classnames';
import Images from './Images.js'
import Whitespace from './Whitespace.js'
import AnalyzedMap from './AnalyzedMap.js';
import AnalyzedInfo from './AnalyzedInfo.js';

class JobInfoCard extends Component {
    render() {
        return(
            <div className="job-info-card">
                <Whitespace header="your images"/>
                <div>
                    <Images />
                </div>
            </div>
        )
    }
}

export default JobInfoCard;
