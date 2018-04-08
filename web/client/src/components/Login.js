import React, { Component } from 'react';
import { Redirect } from 'react-router';
import Dropzone from 'react-dropzone'

class Login extends Component {
    render() {
        return (
            <div className="login-box centered">
                <h2>Pathfinder</h2>
                <LoginForm />
                <FileDrop />
            </div>
        )
    }
}

class LoginForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            jobID: '',
            fireRedirect: false
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
      event.preventDefault();
      //check if job ID is valid
      //  or check if submitted .zip
      //if existeed but no heatmap then
      this.setState({ fireRedirect: true })
    }

    render() {
        return (
            <div className="login-job-id-box">
                <form onSubmit={this.handleSubmit}>
                    <label>
                        Job ID:
                        <input type="number" value={this.state.jobID} onChange={this.handleChange} />
                    </label>
                    <input type="submit" value="Enter" />
                </form>
                {this.state.fireRedirect && (
                  <Redirect to={'/job-page'}/>
                )}
            </div>
        )
    }
}

class FileDrop extends Component {
    constructor(props) {
        super(props);
        this.state = {
            files: [],
        };
    }

    onDrop(acceptedFiles, rejectedFiles) {
        this.setState({
            files: acceptedFiles
        });
        console.log(acceptedFiles);
    }

    render() {
        return (
            <div className="upload-images-box">
                <Dropzone onDrop={(files) => this.onDrop(files)}>
                    <div>Select .zip with images for analysis</div>
                </Dropzone>
            </div>
        );
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
