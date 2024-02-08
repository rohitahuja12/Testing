import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

/*
React.StrictMode may render a component twice.
This may lead to duplicate API calls in development. 
We should ensure this is not the case in production.
 */
root.render(
  <React.StrictMode> 
    <App />
  </React.StrictMode>
);
