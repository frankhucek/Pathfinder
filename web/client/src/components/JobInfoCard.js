import React, { Component } from 'react';
import Images from './Images.js'
import AnalyzedMap from './AnalyzedMap.js'
import AnalyzedInfo from './AnalyzedInfo.js'
import Projection from './Projection.js'
import Whitespace from './Whitespace.js'
import CrowdInfo from './CrowdInfo.js'

class JobInfoCard extends Component {
    constructor(props) {
        super(props);
        this.state = {
            images: props.images,
            heatmap: props.heatmap,
            retailmap: props.retailmap,
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
                            width={this.state.width}
                            images={this.state.images}/>
                }
                {this.state.cardType === "heatmap" &&
                    <AnalyzedMap height={this.state.height}
                                 width={this.state.width}
                                 heatmap={this.state.heatmap}/>
                }
                {this.state.cardType === "overlay" &&
                    <AnalyzedInfo height={this.state.height}
                                  width={this.state.width}
                                  retailmap={this.state.retailmap}/>
                }
                {this.state.cardType === "project" &&
                    <Projection height={this.state.height}
                                  width={this.state.width}/>
                }
                {this.state.cardType === "crowd" &&
                    <CrowdInfo height={this.state.height}
                               width={this.state.width}/>
                }
            </div>
        )
    }
}

export default JobInfoCard;
