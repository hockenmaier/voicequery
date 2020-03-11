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
    
    pushTest = () => {
        console.log('test')
        console.log(this.state.fileList)
        console.log(this.state.fileList.objects.Contents)
    }
    
    renderFileButton(id,object){
        console.log(object.Key)
        return (
            <div>
                <FileButton key={id}
                      name = {object.Key}
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
                            height: 280,
                            width: window.innerWidth/2.3,
                            }}
                    >
                    <h1>Ask Your Data Anything</h1>
                    {fileButtonArray}
                    <button
                        className="submit-button"
                        onClick={this.pushTest}
                        style={{
                            width: window.innerWidth/6
                        }}
                    >Test</button>
                </div>
            </div>
        );
    }
}
export default FileList;