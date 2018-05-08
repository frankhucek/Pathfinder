import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';
import JobPage from './components/JobPage.js';
import './css/default.css';

class Main extends Component {
    constructor(props) {
        super(props);
        this.state = {
            loggedIn: props.loggedIn,
            jobID: null,
            images: null
        };
    }

    render() {
        if (this.state.loggedIn) {
          return(
            <div className="main">
              <JobPage jobID={this.state.jobID}/>
            </div>
          )
        }

        return (
            <Redirect to={'/login'}/>
        )
    }
}

export default Main;
