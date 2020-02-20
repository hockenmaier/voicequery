import React from 'react';
import { Link } from "react-router-dom";
import './file-upload.css';

class FileUpload extends React.Component {
    render(){
        return(
            <div>
                <div className = 'file-upload-box'
                    style={{
                            top: 100,
                            left: 300,
                            height: 150,
                            width: window.innerWidth/2,
                            }}
                    >
                    <h1> upload a new dataset </h1>
                </div>
            </div>
        );
    }
}

export default FileUpload;