import React, { Component } from 'react';

class Whitespace extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            header: props.header,
            side: props.side
        }
    }

  render() {
    return (
        <div>
            <div className="whitespace">
                <h2 className="whitespace-header">{this.state.header}</h2>
            </div>
        </div>
    )
  }
}

export default Whitespace;
