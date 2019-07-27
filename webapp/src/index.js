import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import bubblesPayload from './sample-payloads/bubblesv2.json' 

class layout{
    //properties are created in the initializeLayout() function below
}

function initializeLayout(){
    layout.topbarX = 0;
    layout.topbarY = 0;
    layout.topbarHeight = 70;
    layout.queryTop = 20;
    layout.queryLeft = 30;

    layout.leftMargin = 30;
    layout.topMargin = layout.topbarHeight + 30;
    layout.rightMargin = 30;

    layout.subjectHeight = 380;
    layout.subjectWidth = 300;

    layout.roomBuffer = 20;
    layout.conditionTop = layout.topMargin + layout.subjectHeight + layout.roomBuffer;
    layout.conditionHeight = 380;
    layout.conditionWidth = 300;

    layout.infoHeight = layout.conditionHeight + layout.subjectHeight + layout.roomBuffer;
    layout.infoWidth = 500;

    layout.BubbleRoomLeftMargin = 20;
    layout.BubbleRoomTopMargin = 30;
    layout.BubbleLeftMargin = layout.leftMargin + layout.BubbleRoomLeftMargin;
    layout.BubbleTopMargin = layout.topMargin + layout.BubbleRoomTopMargin;
    layout.conditionBubbleTopMargin = layout.conditionTop + layout.BubbleRoomTopMargin;

    layout.InfoBubbleLeft = window.innerWidth - (layout.infoWidth + layout.rightMargin - layout.BubbleRoomLeftMargin);

    layout.conceptWidth = 235;
    layout.conceptHeight = 235;
}

let bubblesInitialized = false;

//var lastDragStartId = '';
class lastDragStart{
    id = '';
    type = '';
    shiftX = 0;
    shifty = 0;
}

class BubbleDeets{
    constructor(internalId,text,typetext,bubbles,parentBubbleId, xLocation, yLocation,bubsInConcept){
        this.internalID = internalId;
        this.id = getNextBubbleID();
        this.text = text;
        this.type ='bubble ' + typetext;        
        this.bubbles = bubbles;
        this.parentBubbleId = parentBubbleId;
        this.atHome = true;
        if (bubsInConcept){
            this.bubsInConcept = bubsInConcept;
        }else{
            this.bubsInConcept = [];
        }
        if(xLocation){
            this.xLocation = xLocation;
        }else{
            this.xLocation = nextXLocation(this.type,this.id,this.parentBubbleId);
        }
        if(xLocation){
            this.yLocation = yLocation;
        }else{
            this.yLocation = nextYLocation(this.type);
        }
        
    }
}

let nextBubbleID = 0;
function getNextBubbleID(){
    const next = nextBubbleID;
    nextBubbleID++;
    return next.toString();
}

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
        if (this.props.type === 'bubble subject' | this.props.type === 'bubble condition'){
            height = 50;
            width = 120;
        }else if (this.props.type === 'bubble info-field'){
            height = 40;
            width = 150;
        }
        else if (this.props.type === 'bubble info-value'){
            height = 30;
            width = 90;
        }
        else if (this.props.type === 'bubble concept'){
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
        
        return(
            <button 
                id = {this.props.id}
                className = {this.props.type}        
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

class Space extends React.Component{
    constructor(props){
        super(props);
        initializeLayout();
        this.state = {
            bubbles: bubblesPayload,
            sampleQuery: randomSampleQuery(),
            queryInput: '',
          };
        this.handleQueryChange = this.handleQueryChange.bind(this);        
      }

    componentDidMount(){
        // console.log(bubblesPayload);
        // const rawBubs = this.state.bubbles;
        // console.log(rawBubs);
        // const stringifiedBubs = JSON.stringify(rawBubs);
        // console.log(stringifiedBubs);
        // console.log(JSON.parse(stringifiedBubs));
        
        this.initializeBubbles(this.state.bubbles);
        bubblesInitialized = true;        
    }

    initializeBubbles(bubbles){
        //initializing full bubbledeets object for each top-level bubble in incoming payload
        const newBubbles = bubbles.map((bub) => {
            const newBub = new BubbleDeets(bub.internalID,bub.name,bub.type,bub.bubbles,"");

            //Now we do the same for sub-bubbles
            if(newBub.bubbles.length > 0){
                newBub.bubbles = newBub.bubbles.map((intBub) => {
                    const newIntBub = new BubbleDeets(intBub.internalID,intBub.name,intBub.type,intBub.bubbles,newBub.id);
                    return newIntBub;
                })
            }
            return newBub;
        })
        this.setState({
            bubbles: newBubbles
        })
    }

    handleBubbleDragStart(e, id){
        lastDragStart.id = id;
        //console.log(id);
        lastDragStart.shiftX = e.nativeEvent.clientX - e.nativeEvent.srcElement.getBoundingClientRect().left;
        lastDragStart.shiftY = e.nativeEvent.clientY - e.nativeEvent.srcElement.getBoundingClientRect().top;
    }
    handleBubbleDrop(e, id){
        e.nativeEvent.preventDefault();
        const draggedID = lastDragStart.id.toString();
        const droppedID = id;

        if (droppedID === draggedID){
            this.moveBubble(e);
            return;
        }

        const dragged = this.getBubble(draggedID);
        const dropped = this.getBubble(droppedID);        
        
        if (dragged.type === dropped.type){
            console.log('same type');
            return;
        }else if(dragged.type === 'bubble subject' && dropped.type === 'bubble condition'){
            console.log('subject-condtion');
            return;
        }
        else if(dragged.type === 'bubble condition' && dropped.type === 'bubble subject'){
            console.log('condition-subject');
            return;            
        }
        else if(dragged.type === 'bubble info-value' && dropped.type === 'bubble info-field'){
            console.log('value-field');
            return;
        }
        else if(dragged.type === 'bubble info-field' && dropped.type === 'bubble info-value'){
            console.log('field-value');
            return;
        }
        else if(dragged.type !== 'bubble concept' && dropped.type === 'bubble concept'){
            this.addToConcept(dropped,dragged.id);
            return;
        }        
        else{
            console.log('concept creation');
            this.createConcept(dragged,dropped,e)
        }
    }

    getBubble = (id) => {
        const flatBubs = this.bubbleFlattener(this.state.bubbles);
        for (let iter = 0; iter < flatBubs.length; iter++){
            if (flatBubs[iter].id === id){
                return flatBubs[iter];
            }
        }
    }

    createConcept = (dragged,dropped,e) => {
        let newBubbles = this.state.bubbles;
        const newX = e.nativeEvent.clientX - layout.conceptWidth / 2
        const newY = e.nativeEvent.clientY - layout.conceptHeight / 2
        // newBubbles = this.removeBubble(dragged);  //Don't need to do this now that we're just storing ids
        // newBubbles = this.removeBubble(dropped);
        const newbubsInConcept = []
        newbubsInConcept.push(dragged.id);
        newbubsInConcept.push(dropped.id);
        const newConcept = new BubbleDeets('','New Concept','concept',[],'',newX,newY,newbubsInConcept)
        // this.addToConcept(newConcept,dragged.id);
        // this.addToConcept(newConcept,dropped.id);
        newBubbles.unshift(newConcept);        
        
        //TODO:
        //Add dragged,dropped to concept bubbles array
        //Remove dragged and dropped from newBubbles array
        //Move dragged and dropped to new locations (offset up/down?)
        //console.log(newBubbles);
        this.setState({
            bubbles: newBubbles
        })
        this.positionConceptBubbles(newConcept,newX,newY)
    }

    addToConcept = (concept,childID) => {
        let newBubbles = this.state.bubbles;
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].id === concept.id){
                newBubbles[iter].bubsInConcept.push(childID);
            }
        }
        this.setState({
            bubbles: newBubbles
        })
        this.positionConceptBubbles(concept,concept.xLocation,concept.yLocation);
    }

    removeFromConcept = (childID) => {
        let newBubbles = this.state.bubbles;
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].type === 'bubble concept'){
                for (let iter2 = 0; iter2 < newBubbles[iter].bubsInConcept.length; iter2++){
                    if (newBubbles[iter].bubsInConcept[iter2] === childID){
                        newBubbles[iter].bubsInConcept.splice(iter2,1);
                        //now removing concept if it contains no bubs:
                        if(newBubbles[iter].bubsInConcept.length === 0){
                            newBubbles.splice(iter,1);
                        }
                    }
                }
            }
        }
        
        //console.log(newBubbles);
        this.setState({
            bubbles: newBubbles
        })
    }

    removeBubble = (bubbleToRemove) => {
        let newBubbles = this.state.bubbles;        
        for (let outer = 0; outer < newBubbles.length; outer++){    
            if (newBubbles[outer].bubbles.length > 0){
                for (let inner = 0; inner < newBubbles[outer].bubbles.length; inner++){
                    if (newBubbles[outer].bubbles[inner].id === bubbleToRemove.id){
                        newBubbles[outer].bubbles.splice(inner,1);
                    }
                }
            }
            if (newBubbles[outer].id === bubbleToRemove.id){
                newBubbles.splice(outer,1);
            }
        };
        return newBubbles;
    }

    handleWorkRoomDrop(e){
        this.updateAtHome(false);
        this.moveBubble(e);
        this.removeFromConcept(lastDragStart.id.toString())
    }

    updateAtHome(){
        //Todo:
        //update subject or condition bubble's "athome" state and subtract the appropriate count to allow all bubbles below it to shift up when it drags out
    }

    moveBubble(e){
        //console.log('workroom drop, id of dragged bubble is: ' + lastDragStart.id);
        //console.log(e.nativeEvent);        
        const newX = e.nativeEvent.clientX - lastDragStart.shiftX -3; //I don't know why subtracting 3 pixels is necessary but it is to get the shift perfect
        const newY = e.nativeEvent.clientY - lastDragStart.shiftY -3;

        const newBubbles = this.state.bubbles.map((bub) => {
            for (let inner = 0; inner < bub.bubbles.length; inner++){
                if (bub.bubbles[inner].id === lastDragStart.id.toString()){
                    bub.bubbles[inner].xLocation = newX;
                    bub.bubbles[inner].yLocation = newY;
                }
            }
            if (bub.id === lastDragStart.id.toString()){
                bub.xLocation = newX;
                bub.yLocation = newY;
                if(bub.type === 'bubble concept'){
                    this.positionConceptBubbles(bub,newX,newY)
                }
            }
            return bub;
        })

        this.setState({
            bubbles: newBubbles                
        })
    }

    positionConceptBubbles = (concept,X,Y) => {
        let newBubbles = this.state.bubbles;
        const xOffset = 50;
        const yOffset = 80;
        const nextYOffset = 60;
        for (let outer = 0; outer < newBubbles.length; outer++){
            if(concept.bubsInConcept.includes(newBubbles[outer].id)){
                newBubbles[outer].xLocation = X + xOffset;
                newBubbles[outer].yLocation = Y + yOffset + (concept.bubsInConcept.indexOf(newBubbles[outer].id)*nextYOffset);
            }      
            if (newBubbles[outer].bubbles.length > 0){
                for (let inner = 0; inner < newBubbles[outer].bubbles.length; inner++){
                    if(concept.bubsInConcept.includes(newBubbles[outer].bubbles[inner].id)){
                        newBubbles[outer].bubbles[inner].xLocation = X + xOffset;
                        newBubbles[outer].bubbles[inner].yLocation = Y + yOffset + (concept.bubsInConcept.indexOf(newBubbles[outer].bubbles[inner].id)*nextYOffset);
                    }   
                }
            }
        };
        this.setState({
            bubbles: newBubbles                
        })
    }

    handleWorkRoomDragOver(e){
        e.nativeEvent.preventDefault();
        //console.log('workroom dragover');
    }

    handleQueryChange(e){
        this.setState({queryInput: e.target.value})
        this.updateSampleQuery();
    }

    updateSampleQuery(){
        if (this.state.queryInput === ''){
            this.setState({
                sampleQuery: randomSampleQuery(),         
            })
        }
    }
    
    bubbleFlattener(bubbles){
        let flatBubbles = [];        
        for (let outer = 0; outer < bubbles.length; outer++){            
            flatBubbles.push(bubbles[outer]);
            if (bubbles[outer].bubbles.length > 0){
                for (let inner = 0; inner < bubbles[outer].bubbles.length; inner++){
                    flatBubbles.push(bubbles[outer].bubbles[inner]);
                }
            }
        };
        return flatBubbles;
    }

    renderBubble(bub){
        return (
            <Bubble key={bub.id}
                  internalID = {bub.internalId}
                  id= {bub.id}
                  name= {bub.text}
                  type= {bub.type}
                  onDragStart={(event) => this.handleBubbleDragStart(event, bub.id)} 
                  onDrop={(event) => this.handleBubbleDrop(event, bub.id)}
                  xLocation= {bub.xLocation}
                  yLocation={bub.yLocation}
            />
        );
    }


    render(){
        if (!bubblesInitialized){
            return<div className = "space"></div>; //doing this so that render doesn't execute before bubbles are initialized on componentdidmount
        }

        let bubbleArray = [];
        let flatBubbles = this.bubbleFlattener(this.state.bubbles);
        for (let bubblePos = 0; bubblePos < flatBubbles.length; bubblePos++){
            bubbleArray.push(this.renderBubble(flatBubbles[bubblePos]));            
        };
        
        return(
            <div className = "space">                
                <div className = "work-room"
                    onDrop={this.handleWorkRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        height: window.innerHeight,
                        width: window.innerWidth,
                        top: 0,
                        left: 0,
                    }}
                    >
                </div>
                <div className = "top-bar"
                    style={{
                        top: layout.topbarY,
                        left: layout.topbarX,
                        height: layout.topbarHeight,
                        width: window.innerWidth,
                        }}
                ></div>                
                <div className = "subject-room"
                    style={{
                        height: layout.subjectHeight,
                        width: layout.subjectWidth,
                        top: layout.topMargin,
                        left: layout.leftMargin,
                    }}
                    >
                    Unmapped Subjects
                </div>
                <div className = "condition-room"
                    style={{
                        height: layout.conditionHeight,
                        width: layout.conditionWidth,
                        top: layout.conditionTop,
                        left: layout.leftMargin,
                    }}
                    >
                    Unmapped Conditions
                </div>
                <div className = "info-room"
                    style={{
                        height: layout.infoHeight,
                        width: layout.infoWidth,
                        top: layout.topMargin,
                        right: layout.rightMargin,
                    }}
                    >
                    Available Info: rental_transaction Table
                </div>
                {bubbleArray}
                <div className = "query"
                    style={{
                        height: 0,
                        width: 0,
                        top: layout.queryTop,
                        left: layout.queryLeft,
                    }}
                    >
                    <input 
                        className="query-input"
                        type="text"
                        placeholder={this.state.sampleQuery} 
                        onChange={this.handleQueryChange}
                        value={this.state.queryInput}
                    >
                    </input>
                </div>                
            </div>
        );
    }    
}

function randomSampleQuery(){
    let queries = [];
    queries.push("What was my highest utilization edit bay last month?");
    queries.push("How many visitors came on campus during upfronts?");
    queries.push("What was the most popular week to visit the lot last year?");
    queries.push("Which grip assets are most often part of a subrental?");
    queries.push("What was my AWS spend last month?");
    queries.push("How much did I spend on data storage services in Azure this year to date?");
    queries.push("Which department has the highest AWS spend per user?");
    queries.push("Which department has the lowest revenue per square foot?");
    queries.push("How well are the props purchased in the last year renting?");
    const randomInt = Math.floor(Math.random()*queries.length);
    //console.log(queries[randomInt]);
    return queries[randomInt];
}

let subjectCount = 0;
let conditionCount = 0;
let infoFieldCount = 0;

function nextXLocation(type,id,parentId){
    if (type === 'bubble subject' | type === 'bubble condition'){
        return layout.BubbleLeftMargin;
    }else if (type === 'bubble info-field'){
        return layout.InfoBubbleLeft;
    }else if (type === 'bubble info-value'){
        return layout.InfoBubbleLeft + 60 + ((parseInt(id)-parseInt(parentId))*105);
    }else{
    return 300;
    }
}

function nextYLocation(type){
    //console.log(type);
    if (type === 'bubble subject'){
        const nextY =  layout.BubbleTopMargin + subjectCount*60;
        subjectCount++;
        return nextY;
    }
    else if (type === 'bubble condition'){
        const nextY = layout.conditionBubbleTopMargin + conditionCount*60;
        conditionCount++;
        return nextY;
    }
    else if (type === 'bubble info-field'){
        const nextY = layout.BubbleTopMargin + infoFieldCount*55;
        infoFieldCount++;
        return nextY;
    }
    else if (type === 'bubble info-value'){
        const nextY = layout.BubbleTopMargin + (infoFieldCount-1)*55 + 5;
        return nextY;
    }
    else{
        return 300;
    }
    
}

ReactDOM.render(<Space />, document.getElementById('root'));
