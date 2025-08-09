import React from 'react';
import ReactDOM from 'react-dom/client';
import TestApp from './App.test';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <TestApp />
  </React.StrictMode>
);