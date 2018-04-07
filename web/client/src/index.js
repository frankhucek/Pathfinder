import React from 'react';
import ReactDOM from 'react-dom';
import registerServiceWorker from './registerServiceWorker';
import Main from './Main.js';

ReactDOM.render(<Main />, document.getElementById('root'));
registerServiceWorker();
