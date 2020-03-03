import React from 'react';
import { Link } from "react-router-dom";
import './file-select.css';
import FileUpload from './file-upload.js';
import FileList from './file-list.js';

class FileSelect extends React.Component {
    render(){
        return(
            <div>
                <div className = 'title'>
                    <h1>The Answering Machine</h1>
                
                    <FileUpload />
                    <FileList />
                
                    <Link to="/space">Go to Workspace</Link>
                </div>
            </div>
        );
    }
}

export default FileSelect;