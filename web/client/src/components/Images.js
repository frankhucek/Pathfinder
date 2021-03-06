import React, { Component } from 'react';
import Slider from 'react-slick';
import Image from 'react-image-resizer';

class Images extends Component {
  constructor(props) {
    super(props);

    this.state = {
        jobID: props.jobID,
        images: [],
        height: props.height,
        width: props.width,
    }
  }

  componentDidMount() {
    this.getImageFileNames()
      .then(res => {
          for (var image in res.images) {
            var img_file = '/job/' + this.state.jobID + '/image/' + res.images[image];
            var joined = this.state.images.concat(
              <div><Image
                src={img_file}
                height={ this.state.height }
                width={ this.state.width }
              /></div>
            );
            this.setState({ images: joined });
          }
      });
  }

  getImage = async (image) => {
    const file = '/job/' + this.state.jobID + '/image/' + image;
    const response = await fetch(file);

    return response;
  };

  getImageFileNames = async () => {
    const filenames = /job/ + this.state.jobID + '/allimages/';
    const response = await fetch(filenames);
    const body = response.json();

    return body;
  };

  render() {
    const sliderSettings = {
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 1,
        slidesToScroll: 1,
    };

    return(
        <div className="image-display">
          <Slider {... sliderSettings}>
              { this.state.images }
          </Slider>
        </div>
    );
  }
}

export default Images;
