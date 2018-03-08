import React, { Component } from 'react';
import Slider from 'react-slick';
import job_image_1 from '../data/1.jpg';
import job_image_2 from '../data/2.jpg';

class Images extends React.Component {
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
          slidesToScroll: 1
      };

      return(
          <div>
            {/*Add images from GoPro or submitted images from .zip*/}
            <Slider {... sliderSettings}>
                <div><img src={job_image_1}/></div>
                <div><img src={job_image_2}/></div>
            </Slider>
          </div>
      );
  }
}

export default Images;
