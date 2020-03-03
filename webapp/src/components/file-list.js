import React, {useCallback} from 'react'
import { Link } from "react-router-dom";
import './file-select.css';
import axios from 'axios';

class FileList extends React.Component {
    constructor(props){
        super(props);
    }
    render(){
        return(
            <div>
                <div className = 'file-upload-box'
                    style={{
                            top: 100,
                            left: 300,
                            height: 280,
                            width: window.innerWidth/2.3,
                            }}
                    >
                    <h1>Ask Your Data Anything</h1>
                </div>
            </div>
        );
    }
}
export default FileList;