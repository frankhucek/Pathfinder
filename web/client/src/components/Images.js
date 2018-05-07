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

  importAllImages(filepath) {
    var images = [];
    
    return images;
  }

  componentDidMount() {
    var filepath = /job/ + this.state.jobID + '/image/';
    var all_images = this.importAllImages(filepath);
    for (var image in all_images) {
      var res = this.getImage(image);
      var complete_link = 'http://localhost:4000' + res;
      var joined = this.state.images.concat(
        <div><Image
          src={complete_link}
          height={ this.state.height }
          width={ this.state.width }
        /></div>
      );
      this.setState({ images: joined });
    }
  }

  getImage = async (image) => {
    const image_get = /job/ + this.state.jobID + '/image/' + image;
    const response = await fetch(image_get);

    return image_get;
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
