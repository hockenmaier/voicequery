import React from 'react';
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
                    <FileList selectWorkSpace = {this.props.selectWorkSpace}/>
                </div>
            </div>
        );
    }
}

export default FileSelect;