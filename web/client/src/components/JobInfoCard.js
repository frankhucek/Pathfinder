import React, { Component } from 'react';
import Images from './Images.js'
import AnalyzedMap from './AnalyzedMap.js'
import Whitespace from './Whitespace.js'

class JobInfoCard extends Component {
    constructor(props) {
        super(props);
        this.state = {
            cardType: props.cardType,
            header: props.header,
            height: 324,
            width: 432
        }
    }

    render() {
        return(
            <div className="job-info-card">
                <Whitespace header={this.state.header}/>
                {this.state.cardType === "images" &&
                    <Images height={this.state.height}
                            width={this.state.width}/>
                }
                {this.state.cardType === "heatmap" &&
                    <AnalyzedMap height={this.state.height}
                                 width={this.state.width}/>
                }
            </div>
        )
    }
}

export default JobInfoCard;
