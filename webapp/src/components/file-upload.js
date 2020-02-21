import React, {useCallback} from 'react'
import { Link } from "react-router-dom";
import './file-upload.css';
import {useDropzone} from 'react-dropzone'


function MyDropzone() {
  const onDrop = useCallback(acceptedFiles => {
    console.log(acceptedFiles)
  }, [])
  const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop})
 
  return (
    <div className = 'drop-box'>
        <div {...getRootProps()}>
          <input {...getInputProps()} />
          {
            isDragActive ?
              <p>Drop the files here ...</p> :
              <p>Drag 'n' drop some files here, or click to select files</p>
          }
        </div>
    </div>
  )
}

class FileUpload extends React.Component {
    
    render(){
                return(
            <div>
                <div className = 'file-upload-box'
                    style={{
                            top: 100,
                            left: 300,
                            height: 150,
                            width: window.innerWidth/2,
                            }}
                    >
                    <h1>Upload a new dataset</h1>
                    <MyDropzone />
                </div>
            </div>
        );
    }
}

export default FileUpload;