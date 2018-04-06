import React, { Component } from 'react';

class Whitespace extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            header: props.header,
        }
    }

  render() {
    return (
        <div className="whitespace">
            <h2 className="whitespace-header">{this.state.header}</h2>
        </div>
    )
  }
}

export default Whitespace;
