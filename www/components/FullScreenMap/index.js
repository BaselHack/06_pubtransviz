import React, { Component } from 'react'
import ReactMapGL from 'react-map-gl'

export default class FullScreenMap extends Component{
  constructor(props) {
    super(props)
    this.state = {
    }
  }

  render() {
    return (
      <ReactMapGL
        // width={400}
        height={700}
        latitude={47.559601}
        longitude={7.588576}
        zoom={12}
        onViewportChange={(viewport) => {
          const { width, height, latitude, longitude, zoom } = viewport
          // Optionally call `setState` and use the state to update the map.
        }}
        style={{
          width: '100%'
        }}
      />
    )
  }
}
