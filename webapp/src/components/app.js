import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import Space from './space.js';
import FileSelect from './file-select.js';
import { Link } from "react-router-dom";
import { Redirect } from 'react-router-dom';

export default class App extends React.Component {
  constructor(props){
      super(props);
      this.state = {
        workspace: '',
        redirected: false,
      };
  }
  
  selectWorkSpace = (workspace) => {
    this.setState({
      workspace: workspace,
    })
    // console.log('At app component and workspace was just set to: ' + workspace)
  }
  
  render(){
    if (this.state.redirected){
      return (
      <Router>
        <div>
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
    }else{
      this.setState({
        redirected: true,
      })
      return(
        <Router>
          <Redirect push to="/"/>
        </Router>
      );
    }
  }
}