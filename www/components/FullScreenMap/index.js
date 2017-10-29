/* global window */
import React, {Component} from 'react';
import {render} from 'react-dom';
import MapGL, {Marker} from 'react-map-gl';
import ControlPanel from './control-panel';

import { json as requestJson } from 'd3-request'

import tramStations from './bart-station.json';

const MAPBOX_TOKEN = process.env.MAPBOX_TOKEN; // Set your mapbox token here
import MARKER_STYLE from './marker-style';

export default class App extends Component {

  constructor(props) {
    super(props)
    this.state = {
      tramStations: [],
      viewport: {
        latitude: 47.559601,
        longitude: 7.588576,
        zoom: 11,
        bearing: 0,
        pitch: 50,
        width: 500,
        height: 500
      },
      settings: {
        dragPan: true,
        dragRotate: true,
        scrollZoom: true,
        touchZoomRotate: true,
        doubleClickZoom: true,
        minZoom: 0,
        maxZoom: 20,
        minPitch: 0,
        maxPitch: 85
      },
      stylemapbox: 'mapbox://styles/mapbox/streets-v9'
    }

    this._resize = this._resize.bind(this)
  }

  componentDidMount() {
    window.addEventListener('resize', this._resize);

    requestJson('http://localhost:8080/api/v1/stations', (error, response) => {

      console.log(response)

      if (!error) {
        this.setState({tramStations: response});
      }
    });


    this._resize();
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this._resize);
  }

  _resize() {
    this.setState({
      viewport: {
        ...this.state.viewport,
        width: this.props.width || window.innerWidth,
        height: this.props.height || window.innerHeight
      }
    })
  }

  _onViewportChange = viewport => this.setState({viewport});

  _onSettingChange = (name, value) => this.setState({
    settings: {...this.state.settings, [name]: value}
  });

  _renderMarker(station, i) {
    const {name, coordinates} = station;
    return (
      <Marker key={i} longitude={coordinates[0]} latitude={coordinates[1]} >
        <div className="station"><span>{name}</span></div>
      </Marker>
    );
  }

  render() {

    const {
      viewport,
      settings,
      stylemapbox,
      tramStations
    } = this.state;

    return (
      <MapGL
        {...viewport}
        {...settings}
        mapStyle={stylemapbox}
        onViewportChange={this._onViewportChange}
        mapboxApiAccessToken={MAPBOX_TOKEN} >
        <style>{MARKER_STYLE}</style>
        { tramStations.map(this._renderMarker) }
        <ControlPanel containerComponent={this.props.containerComponent}
          settings={settings} onChange={this._onSettingChange} />
      </MapGL>
    );
  }

}
