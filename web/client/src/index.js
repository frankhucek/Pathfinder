import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import registerServiceWorker from './registerServiceWorker';
import Main from './Main.js';
import Login from './components/Login.js'

ReactDOM.render(
  <Router>
    <div>
      <Route path='/' component={Main} />
    </div>
  </Router>
  , document.getElementById('root')
);
registerServiceWorker();
