import React from 'react';
import {lastDragStart, layout} from './helpers.js';

class Bubble extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            dragover: false,
        };
    }
    
    handleDragOver(e){
        e.preventDefault();
        let dragover = true;
        //console.log('target id is: ' + e.nativeEvent.target.id + ' and this.props.id is: ' + this.props.id + ' and global lasdragstartid is: ' + lastDragStartId);
        
        if (e.nativeEvent.srcElement.id === lastDragStart.id.toString()){
            dragover = false;
        }
        this.setState({
            dragover: dragover,
        })
    }
    handleDragLeave(e){
        this.setState({
            dragover: false,
        })
    }

    // handleDragStart(e){
    //     console.log('drag start and this.props.id is: ' + this.props.id);
    // }

    render(){
        //set base size by type        
        let height;
        let width;
        if (this.props.type === 'subject' | this.props.type === 'condition'){
            height = 50;
            width = 120;
        }else if (this.props.type === 'info-field'){
            height = 40;
            width = 150;
        }
        else if (this.props.type === 'info-value'){
            height = 30;
            width = 90;
        }
        else if (this.props.type === 'concept'){
            height = layout.conceptHeight;
            width = layout.conceptWidth;
        }     
        //modify size based on dragover event
        const dragScale = 1.25;
        height = (this.state.dragover ? height*dragScale : height);
        width = (this.state.dragover ? width*dragScale : width);
        
        //turn size into strings
        const stringHeight = (height + 'px');
        const stringWidth = (width + 'px');

        //set base location based on props
        let yLocation = this.props.yLocation;
        let xLocation = this.props.xLocation;
        
        //modify location based on scale (so that expanding bubbles appear to expand fromt the center)
        yLocation = (this.state.dragover ? yLocation - (height * (dragScale-1) / 2.5) : yLocation);  //according to my math we should be dividing by 2 in there instead of 2.5
        xLocation = (this.state.dragover ? xLocation - (width * (dragScale-1) / 2.5) : xLocation);  //I don't know why we have to use 2.5 but we do to get it pixel-perfect and this range of dragscales

        //turn location into strings
        const stringYLocation = yLocation + 'px';
        const stringXLocation = xLocation + 'px';

        const typeBubble= 'bubble ' + this.props.type
        
        return(
            <button 
                id = {this.props.id}
                className = {typeBubble}      
                draggable="true" 
                onDragStart={this.props.onDragStart}
                //onDragStart={this.handleDragStart.bind(this)}
                onDrop={this.props.onDrop}
                onDragOver={this.handleDragOver.bind(this)}
                onDragLeave={this.handleDragLeave.bind(this)}
                style={{
                    height: stringHeight,
                    width: stringWidth,
                    top: stringYLocation,
                    left: stringXLocation,
                }}
            >{this.props.name}
            </button>
        );
    }
}

export default Bubble;