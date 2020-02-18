import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
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

function Home() {
  return (
    <div>
      <h2>Home</h2>
    </div>
  );
}

function SpaceLink() {
  return (
    <div>
      <h2>Space</h2>
    </div>
  );
}
