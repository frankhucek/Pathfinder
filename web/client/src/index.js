import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import registerServiceWorker from './registerServiceWorker';
import Main from './Main.js';
import Login from './components/Login.js'
import JobPage from './components/JobPage.js'

ReactDOM.render(
  <Router>
    <div>
      <Route exact path='/' component={Main} />
      <Route exact path='/login' component={Login} />
      <Route exact path='/job' component={JobPage} />
    </div>
  </Router>
  , document.getElementById('root')
);
registerServiceWorker();
