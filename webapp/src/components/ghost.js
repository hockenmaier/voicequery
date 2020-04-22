import React from 'react';
import {lastDragStart, layout} from './helpers.js';

class Ghost extends React.Component{
    constructor(props){
        super(props);
    }
    
    render(){
        //set base size by type        
        let height = layout.bubbleHeight[this.props.ghostType];
        let width = layout.bubbleWidth[this.props.ghostType];
        //turn size into strings
        const stringHeight = (height + 'px');
        const stringWidth = (width + 'px');
        
        //set subtext
        let subText = ''
        if (this.props.ghostType === 'info-value'){
            subText = '\n' + '(' + this.props.parentFieldName + ')'
        }else{
            subText = ''
        }

        //set location based on props
        let yLocation = this.props.yLocation;
        let xLocation = this.props.xLocation;
        //turn location into strings
        const stringYLocation = yLocation + 'px';
        const stringXLocation = xLocation + 'px';

        let typeBubble = this.props.room + '-position bubble ' + this.props.type //3 Styles here: room-position, bubble, and type
        let titleClass = typeBubble + '-title' //1 Style here: type-title
        let typeGhost = this.props.room + '-position ghost ' + this.props.ghostType + '-ghost'
        
        
        return(
            <button 
                id = {this.props.id}
                className = {typeGhost}      
                draggable="false" 
                style={{
                    height: stringHeight,
                    width: stringWidth,
                    top: stringYLocation,
                    left: stringXLocation,
                }}
            ><span className={titleClass}>{this.props.name}</span>
            <span className='subtitle'>{subText}</span>
            </button>
        );
    }
}

export default Ghost;
