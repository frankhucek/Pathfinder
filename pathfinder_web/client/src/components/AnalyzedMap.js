var React = require('react');

class AnalyzedMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
        mapType: this.props.mapType
    }
  }

  render() {
      return (
          <div>
              {/*Add image of heatmap or coordinate mappping and possible interaction*/}
          </div>
      )
  }
}

export default AnalyzedMap;
