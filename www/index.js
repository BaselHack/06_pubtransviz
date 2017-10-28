import { createDevTools } from 'redux-devtools'
import LogMonitor from 'redux-devtools-log-monitor'
import DockMonitor from 'redux-devtools-dock-monitor'

import React from 'react'
import ReactDOM from 'react-dom'
import { createStore, combineReducers } from 'redux'
import { Provider } from 'react-redux'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import { createBrowserHistory } from 'history'

import * as reducers from './reducers'
import {
  Main
} from './components'

import './styles/base.scss'

const reducer = combineReducers({
  ...reducers
})

const DevTools = createDevTools(
  <DockMonitor toggleVisibilityKey='ctrl-h' changePositionKey='ctrl-q'>
    <LogMonitor theme='tomorrow' preserveScrollTop={false} />
  </DockMonitor>
)

const store = createStore(
  reducer,
  DevTools.instrument()
)

const history = createBrowserHistory()

const ReduxApp = (
  <Provider store={store}>
    <div>
      {/* <DevTools /> */}
      <Router history={history}>
        <Switch>
          <Route exact name='home' path='/' component={Main} />
        </Switch>
      </Router>
    </div>
  </Provider>
)

ReactDOM.render(ReduxApp, document.getElementById('root'))
