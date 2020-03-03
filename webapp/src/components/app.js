import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import Space from './space.js';
import FileSelect from './file-select.js';

export default class App extends React.Component {
  constructor(props){
      super(props);
      this.state = {
          workspace: '',
      };
  }
  render(){
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
}