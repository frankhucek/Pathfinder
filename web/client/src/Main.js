import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Link,
  Redirect
} from 'react-router-dom';
import Login from './components/Login.js';
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
              <JobPage images={this.state.images}
                        jobID={this.state.jobID}/>
            </div>
          )
        }

        return (
            <Redirect to={'/login'}/>
        )
    }
}

export default Main;
