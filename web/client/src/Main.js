import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Link
} from 'react-router-dom';
import Login from './components/Login.js';
import JobPage from './components/JobPage.js';
import './css/default.css';

class Main extends Component {
    constructor(props) {
        super(props);
        this.state = {
            loggedIn: props.loggedIn
        };
    }

    render() {
        let content = null;
        if (this.state.loggedIn) {
            content = <JobPage/>;
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
