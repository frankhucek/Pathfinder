import React, { Component } from 'react';
import Image from 'react-image-resizer';

class Projection extends Component {
    constructor(props) {
        super(props);

        this.state = {
            height: props.height,
            width: props.width,
            project: '',
        }
    }

    componentDidMount() {
      this.getProjection()
        .then(res => this.setState({ project : res }));
    }

    getProjection = async () => {
      const file = '/job/' + this.state.jobID + '/projection/';
      const response = await fetch(file);

      return response;
    };

  render() {
      return (
        <div>
          <div className="image-display">
              <div><Image
                    src={this.state.project}
                    height={ this.state.height }
                    width={ this.state.width }
              /></div>
          </div>
        </div>
      )
  }
}

export default Projection;
