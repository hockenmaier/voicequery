import React, {useCallback} from 'react'
import { Link } from "react-router-dom";
import './file-select.css';
import axios from 'axios';

class FileList extends React.Component {
    constructor(props){
        super(props);
    }
    
    getFileList = () =>{
         axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/get-datasets', {
            userID: 'voicequery-user',
        },
        )
        .then(function(response){
            console.log('get datasets http successful');
            console.log(response);
            return response.data.objects;
        })
        .catch(function(error){
            console.log('get datasets http error');
            console.log(error);
        });
    }
    
    render(){
        
        this.getFileList();
        
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