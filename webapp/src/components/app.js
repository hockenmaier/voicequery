import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import Space from './space.js';
import FileSelect from './file-select.js';
import { Link } from "react-router-dom";

export default class App extends React.Component {
  constructor(props){
      super(props);
      this.state = {
        workspace: '',
      };
  }
  
  selectWorkSpace = (workspace) => {
    this.setState({
      workspace: workspace,
    })
    // console.log('At app component and workspace was just set to: ' + workspace)
  }
  
  render(){
    return (
      <Router>
        <div>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/space">Space</Link>
            </li>
            <li>
              <Link to="/dashboard">Dashboard</Link>
            </li>
          </ul>
          <Switch>
            <Route exact path="/">
              <FileSelect
                selectWorkSpace = {this.selectWorkSpace}
                workspace = {this.state.workspace}
              />
            </Route>
            <Route path="/space">
              <Space
                workspace = {this.state.workspace}
              />
            </Route>
          </Switch>
        </div>
      </Router>
    );
  }
}