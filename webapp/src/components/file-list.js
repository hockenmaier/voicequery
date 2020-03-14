import React from 'react'
import { Link } from "react-router-dom";
import './file-select.css';
import FileButton from './file-button.js';
import axios from 'axios';

class FileList extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            fileList: undefined,
        };
    }
    
    componentDidMount(){
        this.getFileList();
        console.log('mounted')
    }
    
    getFileList = () =>{
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/get-datasets', {
            userID: 'voicequery-user',
        },
        )
        .then(function(response){
            console.log('get datasets http successful');
            console.log(response);
            var parsedData = JSON.parse(response.data);
            self.setState({
                fileList: parsedData,
            })
        })
        .catch(function(error){
            console.log('get datasets http error');
            console.log(error);
        });
    }
    
    renderFileButton(id,object){
        console.log(id)
        console.log(object.Key)
        let s3KeySplit = object.Key.split("/")
        return (
            <div>
                <FileButton key={id}
                      workspace = {s3KeySplit[1]}
                      fullfilename = {s3KeySplit[2]}
                />
                <br/>
            </div>
        );
    }
    
    render(){
        
        let fileButtonArray = [];
        if(this.state.fileList != undefined){
            let id;
            for (id in this.state.fileList.objects.Contents){
                fileButtonArray.push(this.renderFileButton(id,this.state.fileList.objects.Contents[id]));
            }
        }
        
        return(
            <div>
                <div className = 'file-upload-box'
                    style={{
                            top: 100,
                            left: 300,
                            width: window.innerWidth/2.3,
                            }}
                    >
                    <h1>Ask Your Data Anything</h1>
                    {fileButtonArray}
                </div>
            </div>
        );
    }
}
export default FileList;