import React from 'react'
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
            var parsedData = JSON.parse(response.data);
            console.log(parsedData);
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
        // console.log(id)
        // console.log(object.Key)
        let s3KeySplit = object.Key.split("/")
        let s3LastModifiedSplit = object.LastModified.split(" ")
        return (
            <div>
                <FileButton key={id}
                    s3objectKey = {object.Key}
                    workspace = {s3KeySplit[1]}
                    fullfilename = {s3KeySplit[2]}
                    selectWorkSpace = {this.props.selectWorkSpace}
                    uploadDate = {s3LastModifiedSplit[0]}
                />
                <br/>
            </div>
        );
    }
    
    render(){
        
        let fileButtonArray = [];
        if(this.state.fileList !== undefined){
            let id;
            let sortedFileList = this.state.fileList.objects.Contents.sort((a, b) => (a.LastModified < b.LastModified) ? 1 : -1)
            for (id in sortedFileList){
                fileButtonArray.push(this.renderFileButton(id,sortedFileList[id]));
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