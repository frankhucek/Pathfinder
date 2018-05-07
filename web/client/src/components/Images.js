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
          console.log(res.images)
          for (var image in res.images) {
            var img_file = this.getImage(res.images[image]);
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

  getImage(image) {
    return 'http://localhost:4000/job/' + this.state.jobID + '/image/' + image;
  }

  getImageFileNames = async () => {
    const filenames = /job/ + this.state.jobID + '/allimages/';
    console.log(filenames);
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
