import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
import Space from './space.js';

export default function App() {
  return (
    <Router>
      <div>
        <Link to="/space">Go to Workspace</Link>
        <hr />
        <Switch>
          <Route exact path="/">
            <Home />
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
