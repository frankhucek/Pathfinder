import React, { Component } from 'react';
import './css/default.css';
import Login from './components/Login.js';

class Main extends Component {
    render() {
        return (
            <html>
                <head>
                    <link href="https://fonts.googleapis.com/css?family=Kameron" rel="stylesheet"/>
                </head>
                <body>
                    <div className="root">
                        <Login />
                    </div>
                </body>
            </html>
        )
    }
}

export default Main;
