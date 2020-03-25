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
                        height: window.innerHeight/20,
                    }}
                    ><span className='workspaceText'>{this.props.workspace}</span>
                    <div className='fileNameText'>{this.props.fullfilename}</div><div className='dateText'>Uploaded  {this.props.uploadDate}</div>
                    <Link to="/"
                        className="file-delete"
                        style={{
                            top: -25,
                            left: 2,
                            width: window.innerHeight/28,
                            height: window.innerHeight/28,
                        }}
                        ><img src={require('../img/small-delete-can.png')} alt="Delete File" onClick={this.clickDelete} />
                    </Link>
                </button>
                </Link>
                
            </div>
        );
    }
}
export default FileButton;