/* global window,document */
import React, { Component } from 'react'
import { render } from 'react-dom'
import MapGL from 'react-map-gl'
import DeckGLOverlay from './deckgl-overlay.js'

import { json as requestJson } from 'd3-request'

// Set your mapbox token here
const MAPBOX_TOKEN = process.env.MAPBOX_TOKEN; // eslint-disable-line

// Source data CSV
const DATA_URL = {
  AIRPORTS: 'https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/line/airports.json',  // eslint-disable-line
  FLIGHT_PATHS: 'https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/line/heathrow-flights.json'  // eslint-disable-line
}

export default class DeckGLLines extends Component {

  constructor(props) {
    super(props)
    this.state = {
      viewport: {
        ...DeckGLOverlay.defaultViewport,
        width: 500,
        height: 500
      },
      flightPaths: null,
      airports: null
    };

    requestJson('http://localhost:8080/api/v1/connections', (error, response) => {
      if (!error) {
        this.setState({ flightPaths: response });
      }
    })
    // requestJson(DATA_URL.AIRPORTS, (error, response) => {
    //   if (!error) {
    //     this.setState({airports: response});
    //   }
    // });
  }

  componentDidMount() {
    window.addEventListener('resize', this._resize.bind(this));
    this._resize();
  }

  _resize() {
    this._onViewportChange({
      width: window.innerWidth,
      height: window.innerHeight
    });
  }

  _onViewportChange(viewport) {
    this.setState({
      viewport: {...this.state.viewport, ...viewport}
    });
  }


  render() {
    const {viewport, flightPaths, airports} = this.state;

    return (
      <MapGL
        {...viewport}
        mapStyle='mapbox://styles/mapbox/streets-v9'
        onViewportChange={this._onViewportChange.bind(this)}
        mapboxApiAccessToken={MAPBOX_TOKEN}>
        <DeckGLOverlay viewport={viewport}
          strokeWidth={2}
          flightPaths={flightPaths}
          airports={airports} />
      </MapGL>
    );
  }
}
