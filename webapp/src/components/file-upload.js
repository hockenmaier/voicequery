import React, {useCallback} from 'react'
import { Link } from "react-router-dom";
import './file-upload.css';
import {useDropzone} from 'react-dropzone'


function FileDropzone() {
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
            // sendFile(fileSelected)
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

class FileUpload extends React.Component {
    
    sendFile(file){
        console.log('sending file');
        console.log(file)
    }
    
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
                    <FileDropzone />
                </div>
            </div>
        );
    }
}

export default FileUpload;