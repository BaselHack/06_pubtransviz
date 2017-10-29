import React, { Component } from 'react'
import { TabGroup, Tab } from 'material-tabs'

import FullScreenMap from './FullScreenMap'
import DeckGLMap from './DeckGLMap'

const tabs = [
  { linkTo: 'map', label: 'Map' },
  { linkTo: 'heatmap', label: 'Heatmap' }
]

class Main extends Component {

  constructor(props) {
    super(props)
    this.state = {
      visibleTab: 0
    }


    this.handleChange = this.handleChange.bind(this)
  }

  renderTabs() {
    return tabs.map(tab => {
      return (
        // <UnstyledLink to={tab.linkTo} key={index}>
        <Tab key='tab.label' style={{ color: 'white' }}>
          {tab.label}
        </Tab>
        // </UnstyledLink>
      )
    })
  }

  handleChange(index) {
    this.setState({
      visibleTab: index
    })
  }


  render() {

    const {
      visibleTab
    } = this.state

    return (
      <div style={{ backgroundColor: '#2c3e50' }}>
        <br />
        <h3 style={{ color: 'white', textAlign: 'center', fontWeight: '500' }}>
          Public Transport Visualization
        </h3>
        <br />
        <TabGroup style={{ indicator: { color: '#2196f3' } } } onChangeTab={this.handleChange}>
          {this.renderTabs()}
        </TabGroup>

        {visibleTab === 0 ?
          <FullScreenMap />
          : null }
        {visibleTab === 1 ?
          <DeckGLMap />
          : null }

      </div>
    )
  }
}

export { Main }
