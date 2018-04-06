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
            images: null
        }
    }

  render() {
      const sliderSettings = {
          dots: true,
          infinite: true,
          speed: 500,
          slidesToShow: 1,
          slidesToScroll: 1,
          className: 'image-slide'
      };

      return(
          <div className="slider">
            {/*Add images from GoPro or submitted images from .zip*/}
            <Slider {... sliderSettings}>
                <div><img src={job_image_0}/></div>
                <div><img src={job_image_1}/></div>
                <div><img src={job_image_2}/></div>
            </Slider>
          </div>
      );
  }
}

export default Images;
