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
    
    handleDrop(e){
        this.setState({
            dragover: false,
        })
        this.props.onDrop(e)
    }
    
    getConceptTexts(){
        let conceptTexts = {
            'subject': '',
            'condition': '',
            'info-field': '',
            'info-value': '',
        }
        let item;
        if (this.props.room === 'concept'){
            for (item in this.props.conceptBubbles){
                conceptTexts[this.props.conceptBubbles[item].type] += '\n' + this.props.conceptBubbles[item].text;
            }
        }
        return conceptTexts;
    }
    
    render(){
        //set base size by type        
        let height;
        let width;
        if (this.props.type === 'concept'){
            if (this.props.shrink){
                height = 20 + (this.props.conceptBubbles.length * 50)
                width = layout.bubbleWidth['concept'];
            }else{
                height = 30 + (this.props.conceptBubbles.length * 60)
                width = layout.bubbleWidth['concept'];
            }
        }else{
            height = layout.bubbleHeight[this.props.type]
            width = layout.bubbleWidth[this.props.type]
        }
        let subText = ''
        if (this.props.type === 'subject' | this.props.type === 'condition'){
            subText = '\n' + 'close: ' + this.props.closestMatchText
        }
        //modify size based on dragover event
        const dragScale = 1.15;
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

        let typeBubble= this.props.room + '-position bubble ' + this.props.type //3 Styles here: room-position, bubble, and type
        let titleClass = 'title ' + typeBubble + '-title' //1 Style here: type-title
        if (this.props.shrink){
            titleClass = titleClass + ' grow'
            typeBubble = typeBubble + ' shrink'
        }
        
        const conceptTexts = this.getConceptTexts()
        // if (this.props.room === 'concept'){
        //     console.log('conceptTexts')
        //     console.log(conceptTexts)
        // }
        
        return(
            <button 
                id = {this.props.id}
                className = {typeBubble}      
                draggable="true" 
                onDragStart={this.props.onDragStart}
                //onDragStart={this.handleDragStart.bind(this)}
                onDrop={this.handleDrop.bind(this)}
                onDragOver={this.handleDragOver.bind(this)}
                onDragLeave={this.handleDragLeave.bind(this)}
                style={{
                    height: stringHeight,
                    width: stringWidth,
                    top: stringYLocation,
                    left: stringXLocation,
                }}
            ><span className={titleClass}>{this.props.name}</span>
            <span className='subtitle'>{subText}</span>
            <span className='concept-text subject-concept-text'>{conceptTexts['subject']}</span>
            <span className='concept-text condition-concept-text'>{conceptTexts['condition']}</span>
            <span className='concept-text info-field-concept-text'>{conceptTexts['info-field']}</span>
            <span className='concept-text info-value-concept-text'>{conceptTexts['info-value']}</span>
            </button>
        );
    }
}

export default Bubble;