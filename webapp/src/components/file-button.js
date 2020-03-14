import React from 'react'
import { Link } from "react-router-dom";
import './file-select.css';

class FileButton extends React.Component {
    constructor(props){
        super(props);
    }
    
    pushTest = () => {
        console.log('test')
    }
    
    render(){
        
        // console.log(this.state.fileList);
        
        return(
             <button
                className="file-button"
                onClick={this.pushTest}
                style={{
                    width: window.innerWidth/2.5
                }}
                ><span className='workspaceText'>{this.props.workspace}</span>
                <span className='fileNameText'>{this.props.fullfilename}</span>
            </button>
        );
    }
}
export default FileButton;