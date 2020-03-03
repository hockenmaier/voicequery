import React, {useCallback} from 'react'
import './file-select.css';
import {useDropzone} from 'react-dropzone'
import axios from 'axios';

class FileUpload extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            newFile: undefined,
            workspaceNameInput: '',
        };
    }
    
    addFile = (file) => {
        console.log('adding file')
        this.setState({
            newFile: file,
        })
    }

    sendFile = () => {
        if (this.state.newFile == undefined | this.state.workspaceNameInput == ''){
            window.alert("Please select a data file and name it")
        }else{
            let uploadOK = window.confirm("Upload " + this.state.newFile.name + " under the name " + this.state.workspaceNameInput + " for analysis?");
            if (uploadOK){
                this.getPresignedUrl(this.state.newFile, this.state.workspaceNameInput);
            }
        }
    }
    
    getPresignedUrl = (file, workspace) => {
        console.log('Sending call for presigned url to save-dataset API')
        var self = this;
        
        var mime = require('mime-types')
        var fileType = mime.lookup(file.name)
        console.log("type: " + fileType)
        
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/save-dataset', {
            option: 'geturl',
            workspace: workspace,
            filename: file.name,
            filetype: fileType,
        },
        )
        .then(function(response){
            console.log('transcribe get presigned url http successful');
            console.log(response);
            let presignedUrl = response.data.presignedurl;
            let fileName = response.data.fileName;
            self.uploadFile(file,presignedUrl,fileName,fileType);
        })
        .catch(function(error){
            console.log('transcribe get presigned url http error');
            console.log(error);
        });
    }
    
    uploadFile = (file, presignedUrl, fileName, fileType) => {
        console.log('Uploading Dataset File to S3')
        var self = this;
        fetch(presignedUrl, {method: "PUT", body: file, headers: {
            'Content-Type': fileType,
            // 'Workspace': 'test',
            // 'Content-Type': 'multipart/form-data',
        }})
        .then((response) => {
            console.log('fetch upload file http response');
            console.log(response);
        });
    };
    
    handleWorkspaceNameChange = (e) => {
        this.setState({workspaceNameInput: e.target.value})
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
                    <h1>Upload some Data</h1>
                    <FileDropzone addFile={this.addFile} newFile={this.state.newFile}/>
                    <input 
                        className="workspace-name-input"
                        type="text"
                        placeholder="Name your dataset" 
                        onChange={this.handleWorkspaceNameChange}
                        style={{
                            width: window.innerWidth/6,
                        }}
                    >
                    </input> 
                    <br/>
                    <button
                        className="submit-button"
                        onClick={this.sendFile}
                        style={{
                            width: window.innerWidth/6
                        }}
                    >Upload</button>
                </div>
            </div>
        );
    }
}

function FileDropzone(props) {
    const onDrop = useCallback(acceptedFiles => {
        console.log(acceptedFiles)
        let fileSelected;
        if (acceptedFiles.length > 0){
            fileSelected = acceptedFiles[0]
        }else{
            console.log("no files selected")
            return
        }
        props.addFile(fileSelected)
    }, [])
    const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop})
    let fileText = (props.newFile == undefined ? 'Drag and drop a data file (or click to browse)' : props.newFile.name)
    
    return (
        <div>
            <div {...getRootProps()}
                className = 'drop-box'
                style={{
                      top: 100,
                      left: 300,
                      height: 70,
                      width: window.innerWidth/2.5,
                      }}
                >
                <input {...getInputProps()} />
                {
                isDragActive ?
                    <p>Drop here!</p> :
                    <p>{fileText}</p>
                }
            </div>
        </div>
    )
}



export default FileUpload;