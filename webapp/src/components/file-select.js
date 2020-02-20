import React from 'react';
import { Link } from "react-router-dom";
import './file-select.css';
import FileUpload from './file-upload.js';

class FileSelect extends React.Component {
    render(){
        return(
            <div>
                <div className = 'title'>
                    <h1> Answering Machine </h1>
                
                    <FileUpload />
                
                    <Link to="/space">Go to Workspace</Link>
                </div>
            </div>
        );
    }
}

export default FileSelect;