import React from 'react'
import { Link } from "react-router-dom";
import './file-select.css';

class FileButton extends React.Component {
    
    clickWorkSpace = () => {
        this.props.selectWorkSpace(this.props.s3objectKey)
        // console.log('at filebutton layer and sending key: ' + this.props.s3objectKey)
    }
    
    clickDelete = () => {
        let deleteOK = window.confirm("Are you sure you want to permanently delete " + this.props.workspace + " and all underlying data?");
        console.log('clicked delete')
        if (deleteOK){
            this.props.deleteWorkSpace(this.props.s3objectKey, this.props.workspace, this.props.fullfilename)
        }
    }
    
    render(){
        return(
             <div>
                <Link to="/space">
                 <button
                    className="file-button"
                    onClick={this.clickWorkSpace}
                    style={{
                        width: window.innerWidth/2.5,
                        height: 45,
                    }}
                    ><span className='workspaceText'>{this.props.workspace}</span>
                    <div className='fileNameText'>{this.props.fullfilename}</div><div className='dateText'>Uploaded  {this.props.uploadDate}</div>
                    
                </button>
                </Link>
                <div className="file-delete-reference"
                    style={{
                        top: -43,
                        left: 30,
                        width: 0,
                        height: 0,
                    }}
                    >
                    <Link to="/"
                        className="file-delete"
                        style={{
                            top: 0,
                            left: 0,
                            width: window.innerHeight/28,
                            height: window.innerHeight/28,
                        }}
                        ><img src={require('../img/small-delete-can.png')} alt="Delete File" onClick={this.clickDelete} />
                    </Link>
                </div>
            </div>
        );
    }
}
export default FileButton;