import React, { Component } from 'react';
import Login from './components/Login.js';
import JobInfo from './components/JobInfo.js';
import './css/default.css';

class Main extends Component {
    constructor(props) {
        super(props);
        this.state = {
            loggedIn: false
        };
    }

    render() {

        let content = null;
        if (!this.state.loggedIn) {
            content = <JobInfo/>;
        } else {
            content = <Login />;
        }
        return (
            <div className="main">
                {content}
            </div>
        )
    }
}

export default Main;
