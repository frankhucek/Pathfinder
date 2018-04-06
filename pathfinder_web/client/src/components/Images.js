import React, { Component } from 'react';
import Slider from 'react-slick';
import Image from 'react-image-resizer';
import job_image_0 from '../data/0.jpg';
import job_image_1 from '../data/1.jpg';
import job_image_2 from '../data/2.jpg';

class Images extends Component {
    constructor(props) {
        super(props);

        this.state = {
            images: null,
            height: 324,
            width: 432
        }
    }

  render() {
      const sliderSettings = {
          dots: true,
          infinite: true,
          speed: 500,
          slidesToShow: 1,
          slidesToScroll: 1,
      };

      return(
          <div className="slider">
            {/*Add images from GoPro or submitted images from .zip*/}
            <Slider {... sliderSettings}>
                <div><Image
                  src={job_image_0}
                  height={ this.state.height }
                  width={ this.state.width }
                /></div>
                <div><Image
                  src={job_image_1}
                  height={ this.state.height }
                  width={ this.state.width }
                /></div>
                <div><Image
                  src={job_image_2}
                  height={ this.state.height }
                  width={ this.state.width }
                /></div>
            </Slider>
          </div>
      );
  }
}

export default Images;
