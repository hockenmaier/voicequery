import React from 'react';
import { Link } from "react-router-dom";
import './file-select.css';

class FileSelect extends React.Component {
    render(){
        return(
            <div>
                <div className = 'title'>
                    <h1> Answering Machine </h1>
                </div>
                <hr />
                <Link to="/space">Go to Workspace</Link>
            </div>
        );
    }
}

export default FileSelect;