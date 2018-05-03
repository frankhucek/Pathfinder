import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import registerServiceWorker from './registerServiceWorker';
import Main from './Main.js';

ReactDOM.render(
  <Router>
    <div>
      <Route path='/job-page' component={Main} />
      <Route path='/login' component={Main} />
    </div>
  </Router>
  , document.getElementById('root')
);
registerServiceWorker();
