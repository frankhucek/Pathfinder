import React, { Component } from 'react';

class Login extends Component {

    render() {
        return (
            <div className="login-box centered">
                <h2>Pathfinder</h2>
                <LoginForm />

                <div className="job-id-box">

                </div>
                <div className="upload-images-box">

                </div>

            </div>
        )
    }
}

class LoginForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            jobID: ''
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState(
            {jobID: event.target.value}
        );
    }

    handleSubmit(event) {

    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <label>
                    Job ID:
                    <input type="text" value={this.state.jobID} onChange={this.handleChange} />
                </label>
                <input type="submit" value="Enter" />
            </form>
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
