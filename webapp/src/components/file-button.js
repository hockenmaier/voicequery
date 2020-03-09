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
        
        console.log(this.state.fileList);
        
        return(
             <button
                className="submit-button"
                onClick={this.pushTest}
                style={{
                    width: window.innerWidth/6
                }}
            >Sample Workspace</button>
        );
    }
}
export default FileButton;