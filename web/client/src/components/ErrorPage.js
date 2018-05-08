import React, { Component } from 'react';

class ErrorPage extends Component {

  render() {
    return (
      <div className="centered">
        <h1 className="error-page">This job does not exist. Please try another job</h1>
      </div>
    );
  }
}

export default ErrorPage;
