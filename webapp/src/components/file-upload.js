import React, {useCallback} from 'react'
import { Link } from "react-router-dom";
import './file-upload.css';
import {useDropzone} from 'react-dropzone'
import axios from 'axios';

class FileUpload extends React.Component {
    
    sendFile = (file) => {
        this.getPresignedUrl(file);
    }
    
    getPresignedUrl = (file) => {
        console.log('Sending call for presigned url to save-dataset API')
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/save-dataset', {
            option: 'geturl',
            workspace: 'test',
            filename: file.name,
        },
        )
        .then(function(response){
            console.log('transcribe get presigned url http successful');
            console.log(response);
            let presignedUrl = response.data.presignedurl;
            let fileName = response.data.fileName;
            self.uploadFile(file,presignedUrl,fileName);
        })
        .catch(function(error){
            console.log('transcribe get presigned url http error');
            console.log(error);
        });
    }
    
    uploadFile = (file, presignedUrl, fileName) => {
        console.log('Uploading Dataset File to S3')
        var self = this;
        console.log(file.type);
        fetch(presignedUrl, {method: "PUT", body: file, headers: {
            // 'Content-Type': 'audio/wav',
            // 'Workspace': 'test',
            // 'Content-Type': 'multipart/form-data',
        }})
        .then((response) => {
            console.log('fetch upload file http response');
            console.log(response);
        });
    };
    
    render(){
        return(
            <div>
                <div className = 'file-upload-box'
                    style={{
                            top: 100,
                            left: 300,
                            height: 200,
                            width: window.innerWidth/2,
                            }}
                    >
                    <h1>Upload a new dataset</h1>
                    <FileDropzone sendFile={this.sendFile}/>
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
        let uploadOK = window.confirm("Upload " + fileSelected.name + " to the server?");
        if (uploadOK){
            props.sendFile(fileSelected)
        }
    
    }, [])
    const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop})
 
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
                    <p>Drop files here</p> :
                    <p>Drag and drop a data file (or click to browse)</p>
                }
            </div>
        </div>
    )
}



export default FileUpload;