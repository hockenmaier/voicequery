import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import Space from './space.js';
import FileSelect from './file-select.js';

export default function App() {
  return (
    <Router>
      <div>
        <Switch>
          <Route exact path="/">
            <FileSelect />
          </Route>
          <Route path="/space">
            <Space />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}