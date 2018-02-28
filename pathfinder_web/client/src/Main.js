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
        return (
            <Login/>
        )
    }
}

export default Main;
