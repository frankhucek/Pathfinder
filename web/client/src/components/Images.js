import React, { Component } from 'react';
import Slider from 'react-slick';
import Image from 'react-image-resizer';

class Images extends Component {
  constructor(props) {
    super(props);

    this.state = {
        images: null,
        jobID: 0,
        height: props.height,
        width: props.width,
    }
  }

  //https://stackoverflow.com/questions/42118296/dynamically-import-images-from-a-directory-using-webpack/42118728
  //should be doing this https://reactjs.org/docs/lists-and-keys.html
  //but unable to figure out function+require so go with this for now
  importAllImages() {
    const imgFiles = require.context("../data/images", false, /\.(jpg)$/);
    this.state.images = imgFiles.keys().map((item) =>
      <div><Image
        src={imgFiles(item)}
        height={ this.state.height }
        width={ this.state.width }
      /></div>
    );
  }

  render() {
    this.importAllImages();
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
