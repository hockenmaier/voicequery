import React from 'react'
import { Link } from "react-router-dom";
import './file-select.css';

class FileButton extends React.Component {
    constructor(props){
        super(props);
    }
    
    clickWorkSpace = () => {
        this.props.selectWorkSpace(this.props.s3objectKey)
        // console.log('at filebutton layer and sending key: ' + this.props.s3objectKey)
    }
    
    clickDelete = () => {
        console.log('clicked delete')
        this.props.deleteWorkSpace(this.props.s3objectKey)
    }
    
    render(){
        return(
             <div>
                <button><img src={require('../img/small-delete-can.png')} alt="Delete File" onClick={this.clickDelete} /></button>
                <Link to="/space">
                 <button
                    className="file-button"
                    onClick={this.clickWorkSpace}
                    style={{
                        width: window.innerWidth/2.5
                    }}
                    ><span className='workspaceText'>{this.props.workspace}</span>
                    <div className='fileNameText'>{this.props.fullfilename}</div><div className='dateText'>Uploaded  {this.props.uploadDate}</div>
                </button>
                </Link>
            </div>
        );
    }
}
export default FileButton;