import React, { Component } from 'react';

class Login extends Component {

    render() {
        return (
            <div className="login-box centered">
                <h2>Pathfinder</h2>
                <p>JobID</p>
                <div className="job-id-box">

                </div>
                <EnterJobButton />
                <div className="upload-images-box">

                </div>

            </div>
        )
    }
}

class EnterJobButton extends Component {
    constructor(props) {
        super(props);
        this.sendJobId = this.sendJobId.bind(this);
    }

    sendJobId() {
        //pass in job ID or image.zip
    }

    render() {
        return (
            <button onClick={this.sendJobId}>
                Search
            </button>
        )
    }
}

export default Login;
