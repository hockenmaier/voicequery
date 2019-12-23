import React from 'react';
import Bubble from './bubble.js';
import {lastDragStart, layout, initializeLayout} from './helpers.js';
//import bubblesPayload from '../sample-payloads/bubblesv3.json';
//import bubbleUpdatePayload from './sample-payloads/bubbleUpdatev1.json'
import axios from 'axios'

class Space extends React.Component{
    constructor(props){
        super(props);
        initializeLayout();
        this.state = {
            bubbles: [],
            sampleQuery: randomSampleQuery(),
            queryInput: '',
            queryResponseHTML: '',
            workspace: '1',
          };   
      }

    componentDidMount(){
        // console.log(bubblesPayload);
        // const rawBubs = this.state.bubbles;
        // console.log(rawBubs);
        // const stringifiedBubs = JSON.stringify(rawBubs);
        // console.log(stringifiedBubs);
        // console.log(JSON.parse(stringifiedBubs));
        
        this.initializeBubbles(this.state.bubbles);
        this.sendParseLambdaBootMessage()
        bubblesInitialized = true;
    }

    sendParseLambdaBootMessage = () => {
        console.log('Sending lambda boot parse http call')
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/parse', {
            query: '.'
        },
        )
        .then(function(response){
            console.log('http successful')
            console.log(response)
        })
        .catch(function(error){
            console.log('http error')
            console.log(error);
        });
    }

    initializeBubbles(bubbles){        
        // const newBubbles = this.createBubbleDeets(bubbles);
        this.getWorkspaceLexiconBubbles()
        this.getWorkspaceDataBubbles()
        // this.setState({
        //     bubbles: newBubbles
        // })
    }

    getWorkspaceLexiconBubbles = () => {
        console.log('Sending populate http call with query: ' + this.state.workspace)
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/populate', {
            workspace: this.state.workspace
        },
        )
        .then(function(response){
            console.log('populate http successful')
            //console.log(response)
            self.updateBubbles(response.data)
        })
        .catch(function(error){
            console.log('populate http error')
            console.log(error);
        });
    }

    getWorkspaceDataBubbles = () => {
        console.log('Sending read-dataset http call with query: ' + '')
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/read-dataset', {
            workspace: this.state.workspace
        },
        )
        .then(function(response){
            console.log('read-dataset http successful')
            //console.log(response)
            self.updateBubbles(response.data)
        })
        .catch(function(error){
            console.log('read-dataset http error')
            console.log(error);
        });
    }
    
    saveConcept = (concept) => {
        console.log('Sending create/update save_concept http call with internal ID: ' + concept.internalID)
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/save-concept', {
            internal_ID: concept.internalID,
            workspace: this.state.workspace,
            text: concept.text,
            // concept_items: this.getBubbles(concept.bubsInConcept)
            concept_items: concept.bubsInConcept
        },
        )
        .then(function(response){
            console.log('save_concept http successful')
            console.log(response);
            self.updateInternalID(concept.id,response['data']['conceptID'])
        })
        .catch(function(error){
            console.log('save_concept http error')
            console.log(error);
        });
    }
    
    saveDeleteConcept = (concept) => {
        console.log('Sending delete save_concept http call with internal ID: ' + concept.internalID)
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/save-concept', {
            internal_ID: concept.internalID,
            workspace: this.state.workspace,
            text: concept.text,
            concept_items: ''
        },
        )
        .then(function(response){
            console.log('save_concept http successful')
            console.log(response);
        })
        .catch(function(error){
            console.log('save_concept http error')
            console.log(error);
        });
    }

    createBubbleDeets(bubbles){
        //initializing full bubbledeets object for each top-level bubble in incoming payload
        const newBubbles = bubbles.map((bub) => {
            const newBub = new BubbleDeets(bub.internalID,bub.name,bub.type,bub.bubbles,"",bub.closestMatchId,bub.closestMatchText);

            //Now we do the same for sub-bubbles
            if(newBub.bubbles.length > 0){
                newBub.bubbles = newBub.bubbles.map((intBub) => {
                    const newIntBub = new BubbleDeets(intBub.internalID,intBub.name,intBub.type,intBub.bubbles,newBub.id,bub.closestMatchId,bub.closestMatchText);
                    return newIntBub;
                })
            }
            return newBub;
        })
        return newBubbles;
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
        
        
        if(dragged.type === 'concept'){
            return; //don't add concepts to other concepts or create concepts out of concepts
        }   
        else if(dragged.type === 'subject' && dropped.type === 'condition'){
            console.log('subject-condition');
            return;
        }
        else if(dragged.type === 'condition' && dropped.type === 'subject'){
            console.log('condition-subject');
            return;            
        }
        else if(dragged.type === 'info-value' && dropped.type === 'info-field'){
            console.log('value-field');
            return;
        }
        else if(dragged.type === 'info-field' && dropped.type === 'info-value'){
            console.log('field-value');
            return;
        }
        else if(dragged.type !== 'concept' && dropped.type === 'concept'){
            this.addToConcept(dragged, dropped, e);
            return;
        }if (dragged.type === dropped.type){
            if(dragged.type === 'subject' | dragged.type === 'condition'){
                this.createConcept(dragged,dropped,e)
            }
            return; //don't create concepts from same types other than subjects and conditions
        }
        else{
            console.log('concept creation');
            const newConcept = this.createConcept(dragged,dropped,e)
            // this.positionConceptBubbles(newConcept,newConcept.xLocation,newConcept.yLocation)
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
        const draggedParentConcept = this.findConcept(dragged.id);
        const droppedParentConcept = this.findConcept(dropped.id)
        if (draggedParentConcept){
            if(droppedParentConcept && (draggedParentConcept.id === droppedParentConcept.id)){
                console.log('bubbles already in same concept');
                return; //don't create concept if the two bubbles are already in the same concept
            }
            console.log('removing dragged from concept: ' + dragged.id);
            this.removeFromConcept(dragged.id);            
        }
        console.log('removing dropped from concept: ' + dropped.id);
        this.removeFromConcept(dropped.id);

        let newBubbles = this.state.bubbles.slice(0);
        const newX = e.nativeEvent.clientX - layout.bubbleWidth['concept'] / 2
        const newY = e.nativeEvent.clientY - layout.bubbleHeight['concept'] / 2

        const newbubsInConcept = []
        newbubsInConcept.push(dragged.id);
        newbubsInConcept.push(dropped.id);

        const newConcept = new BubbleDeets('','Concept','concept',[],'','','',newX,newY,newbubsInConcept)
        newBubbles.unshift(newConcept);
        this.saveConcept(newConcept);
        console.log(newBubbles);
        this.setState({   // Have to refactor everywhere now since i am actually setting state directly by assigning an array to the state array
            bubbles: newBubbles
        }, this.positionConceptBubbles(newConcept,newX,newY))  //we need to pass positionConceptBubbles as a callback since setState is Async
    }

    addToConcept = (draggedChild,droppedConcept, e) => {
        //TODO
        //Add logic to not be able to add different types of bubbles (conditions to subjects or more than one info)
        const typesInConcept = this.getConceptTypes(droppedConcept);
        const includesConditions = typesInConcept.includes('condition');
        const includesSubjects = typesInConcept.includes('subject');
        const includesInfo = (typesInConcept.includes('info-value') | typesInConcept.includes('info-field'));

        if (draggedChild.type === 'subject' && includesConditions){
            console.log('No subject-condition addition');
            return;
        }
        else if (draggedChild.type === 'condition' && includesSubjects){
            console.log('No condition-subject addition');
            return;
        }
        else if (((draggedChild.type === 'info-value')|(draggedChild.type === 'info-field')) && includesInfo){
            console.log('Too much info addition');
            return;
        }

        this.removeFromConcept(draggedChild.id);
        
        let newBubbles = this.state.bubbles.slice(0);
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].id === droppedConcept.id){
                if (!droppedConcept.bubsInConcept.includes(draggedChild.id)){
                    newBubbles[iter].bubsInConcept.push(draggedChild.id);
                }else{
                    console.log('already in concept');
                }
            }
        }
        this.saveConcept(droppedConcept);
        
        this.setState({
            bubbles: newBubbles
        })
        this.positionConceptBubbles(droppedConcept,droppedConcept.xLocation,droppedConcept.yLocation);
    }

    removeFromConcept = (childID) => {
        let newBubbles = this.state.bubbles;
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].type === 'concept'){
                for (let iter2 = 0; iter2 < newBubbles[iter].bubsInConcept.length; iter2++){
                    if (newBubbles[iter].bubsInConcept[iter2] === childID){
                        newBubbles[iter].bubsInConcept.splice(iter2,1);
                        //now removing concept if it contains no bubs:
                        if(newBubbles[iter].bubsInConcept.length === 0){
                            this.saveDeleteConcept(newBubbles[iter]);
                            newBubbles.splice(iter,1);
                        }else{
                            this.positionConceptBubbles(newBubbles[iter], newBubbles[iter].xLocation, newBubbles[iter].yLocation);
                            this.saveConcept(newBubbles[iter]); //Update the concept with new set of bubbles
                        }
                    }
                }
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }

    removeBubble = (bubbleToRemove) => {
        let newBubbles = this.state.bubbles.slice;        
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
    
    findConcept = (childID) => {
        let bubbles = this.state.bubbles.slice(0);
        for (let iter = 0; iter < bubbles.length; iter++){
            if (bubbles[iter].bubsInConcept.includes(childID)){
                return bubbles[iter];
            }
        }
    }

    getConceptTypes = (concept) => {
        let types = [];
        for (let iter = 0; iter < concept.bubsInConcept.length; iter++){
            const bub = this.getBubble(concept.bubsInConcept[iter]);
            types.push(bub.type);
        }
        return types;
    }

    handleWorkRoomDrop(e){
        this.updateRoom('work');
        this.updateShrink(false);
        this.moveBubble(e);
        this.removeFromConcept(lastDragStart.id.toString());
        // console.log(this.state.bubbles);
    }
    
    handleConceptRoomDrop(e){
        const draggedID = lastDragStart.id.toString();
        const draggedType = this.getBubble(draggedID).type;
        if (draggedType === 'concept'){
            this.updateRoom('concept');
            this.updateShrink(true);
            this.moveBubble(e);
        }
    }
    
    handleSubjectRoomDrop(e){
        const draggedID = lastDragStart.id.toString();
        const draggedType = this.getBubble(draggedID).type;
        if (draggedType === 'subject'){
            this.updateRoom('subject');
            this.removeFromConcept(lastDragStart.id.toString());
        }
    }
    
    handleConditionRoomDrop(e){
        const draggedID = lastDragStart.id.toString();
        const draggedType = this.getBubble(draggedID).type;
        if (draggedType === 'condition'){
            this.updateRoom('condition');
            this.removeFromConcept(lastDragStart.id.toString());
        }
    }

    updateRoom(roomValue){
        const draggedID = lastDragStart.id.toString();
        let newBubbles = this.state.bubbles.slice(0);
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].id === draggedID){
                newBubbles[iter].room = roomValue;
            }
            for (let iter2 = 0; iter2 < newBubbles[iter].bubbles.length; iter2++){
                if (newBubbles[iter].bubbles[iter2].id === draggedID){
                    newBubbles[iter].bubbles[iter2].room = roomValue;
                }
            }
        }
        // for (let outer = 0; outer < newBubbles.length; outer++){            
        //     newBubbles[outer].room = roomValue;
        //     if (newBubbles[outer].newBubbles.length > 0){
        //         for (let inner = 0; inner < newBubbles[outer].newBubbles.length; inner++){
        //             this.getBubble(newBubbles[outer].bubsInConcept[inner]).room = roomValue;
        //         }
        //     }
        // };
        this.setState({
            bubbles: newBubbles
        })
    }
    
    updateShrink(shrinkValue){
        const draggedID = lastDragStart.id.toString();
        let newBubbles = this.state.bubbles.slice(0);
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].id === draggedID){
                newBubbles[iter].shrink = shrinkValue;
                for (let iter2 = 0; iter2 < newBubbles[iter].bubsInConcept.length; iter2++){
                    this.getBubble(newBubbles[iter].bubsInConcept[iter2]).shrink = shrinkValue
                }
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }
    
    updateInternalID(bubbleID, internalID){ //ONLY TOP_LEVEL BUBBLES
        let newBubbles = this.state.bubbles.slice(0);
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].id === bubbleID){
                newBubbles[iter].internalID = internalID;
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }

    moveBubble(e){
        //console.log('workroom drop, id of dragged bubble is: ' + lastDragStart.id);
        //console.log(e.nativeEvent);        
        const newX = e.nativeEvent.clientX - lastDragStart.shiftX; //I don't know why subtracting 3 pixels is necessary but it is to get the shift perfect
        const newY = e.nativeEvent.clientY - lastDragStart.shiftY; //SOLVED: I had a 3 px margin in my main bubble css class!

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
                if(bub.type === 'concept'){
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
        let newBubbles = this.state.bubbles.slice(0);
        // let xOffset = 30;
        let yOffset = 20;
        let nextYOffset = 60;
        if(concept.shrink){
            yOffset = yOffset - 10 + (concept.bubsInConcept).length*14;
            nextYOffset = nextYOffset/2;
        }
        for (let outer = 0; outer < newBubbles.length; outer++){
            if(concept.bubsInConcept.includes(newBubbles[outer].id)){
                let outerBubble = newBubbles[outer];
                outerBubble.xLocation = X + this.getConceptXOffset(outerBubble.type);
                outerBubble.yLocation = Y + yOffset + (concept.bubsInConcept.indexOf(outerBubble.id)*nextYOffset);
                // outerBubble.room = (concept.room == 'concept' ? 'work' : concept.room);
                outerBubble.room = (concept.room);
            }      
            if (newBubbles[outer].bubbles.length > 0){
                for (let inner = 0; inner < newBubbles[outer].bubbles.length; inner++){
                    if(concept.bubsInConcept.includes(newBubbles[outer].bubbles[inner].id)){
                        let innerBubble = newBubbles[outer].bubbles[inner];
                        innerBubble.xLocation = X + this.getConceptXOffset(innerBubble.type);
                        innerBubble.yLocation = Y + yOffset + (concept.bubsInConcept.indexOf(innerBubble.id)*nextYOffset);
                        // innerBubble.room = (concept.room == 'concept' ? 'work' : concept.room);
                        innerBubble.room = (concept.room);
                    }   
                }
            }
        };
        this.setState({
            bubbles: newBubbles                
        })
    }
    
    getConceptXOffset(type){
        let width = layout.bubbleWidth[type];
        return (layout.bubbleWidth['concept'] - width)/2;
    }

    handleWorkRoomDragOver(e){
        e.nativeEvent.preventDefault();
        //console.log('workroom dragover');
    }

    handleQueryChange = (e) => {
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

    handleQuerySubmit = () => {
        console.log('Sending parse http call with query: ' + this.state.queryInput)
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/parse', {
            query: this.state.queryInput
        },
        )
        .then(function(response){
            console.log('http successful')
            //console.log(response)
            self.updateBubbles(response.data)
            self.updateQueryResponse(response.data)
        })
        .catch(function(error){
            console.log('http error')
            console.log(error);
        });
        window.setTimeout(this.detectLambdaBoot,1200);
        //console.log('ask');
        const responseWaitingText = '<p>...</p>';

        this.setState({
            queryResponseHTML: responseWaitingText,                
        })
    }

    detectLambdaBoot = () => {
        if(this.state.queryResponseHTML == '<p>...</p>'){
            const responseWaitingText = '<p>Booting natural language processing server...</p>';

            this.setState({
                queryResponseHTML: responseWaitingText,
            })
        }
    }

    updateBubbles = (data) => {
        console.log(data)
        const stateBubbles = this.state.bubbles.slice(0);
        const newBubbles = this.createBubbleDeets(data.bubbles);
        const allBubbles = stateBubbles.concat(newBubbles);
        this.setState({
            bubbles: allBubbles
        })
    }

    updateQueryResponse = (data) => {
        const responseText = data.htmlResponse;

        this.setState({
            queryResponseHTML: responseText,                
        })
    }
    
    bubbleFlattener(bubbles){
        //console.log(bubbles);
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
    
    getBubbles(ids){
        let bubbleArray = [];
        let id;
        for (id in ids){
            bubbleArray.push(this.getBubble(ids[id]));
        }
        return bubbleArray
    }

    renderBubble(bub){
        const conceptBubbles = this.getBubbles(bub.bubsInConcept)
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
                  closestMatchText={bub.closestMatchText}
                  shrink={bub.shrink}
                  room={bub.room}
                  conceptBubbles={conceptBubbles}
            />
        );
    }


    render(){
        if (!bubblesInitialized){
            return<div className = "space"></div>; //doing this so that render doesn't execute before bubbles are initialized on componentdidmount
        }

        let workRoomBubbleArray = [];
        let subjectRoomBubbleArray = [];
        let conditionRoomBubbleArray = [];
        let infoRoomBubbleArray = [];
        let conceptRoomBubbleArray = [];
        let flatBubbles = this.bubbleFlattener(this.state.bubbles);
        for (let bubblePos = 0; bubblePos < flatBubbles.length; bubblePos++){
            if (flatBubbles[bubblePos].room == 'work')
                workRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos]));
            if (flatBubbles[bubblePos].room == 'subject')
                subjectRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos]));   
            if (flatBubbles[bubblePos].room == 'condition')
                conditionRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos])); 
            if (flatBubbles[bubblePos].room == 'info')
                infoRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos])); 
            if (flatBubbles[bubblePos].room == 'concept')
                if (flatBubbles[bubblePos].type == 'concept'){
                    conceptRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos])); 
                }
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
                <div
                    className="query-response"
                    onDrop={this.handleWorkRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        width: layout.queryResponseWidth,
                        top: layout.queryResponseTop,
                        left: layout.queryResponseLeft,
                    }}
                    dangerouslySetInnerHTML={ {__html: this.state.queryResponseHTML} }
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
                <div className = "room subject-room"
                    onDrop={this.handleSubjectRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        width: layout.lexWidth,
                        top: layout.topMargin,
                        bottom: layout.subjectBottom,
                        left: layout.leftMargin,
                    }}
                    >
                    New Subjects
                    {subjectRoomBubbleArray}
                </div>
                <div className = "room condition-room"
                    onDrop={this.handleConditionRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        width: layout.lexWidth,
                        bottom: layout.bottomMargin,
                        top: layout.conditionTop,
                        left: layout.leftMargin,
                    }}
                    >
                    New Conditions
                    {conditionRoomBubbleArray}
                </div>
                <div className = "room info-room"
                    style={{
                        width: layout.infoWidth,
                        bottom: layout.bottomMargin,
                        top: layout.topMargin,
                        right: layout.rightMargin,
                    }}
                    >
                    Available Info
                    {infoRoomBubbleArray}
                </div>
                <div className = "room concept-room"
                    onDrop={this.handleConceptRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        height: layout.conceptRoomHeight,
                        bottom: layout.conceptRoomBottomMargin,
                        right: layout.conceptRoomRight,
                        left: layout.conceptRoomLeft,
                    }}
                    >
                    Concept Storage
                    {conceptRoomBubbleArray}
                </div>
                {workRoomBubbleArray}
                <div className = "query"
                    >
                    <input 
                        className="query-input"
                        type="text"
                        placeholder={this.state.sampleQuery} 
                        onChange={this.handleQueryChange}                        
                        value={this.state.queryInput}
                        style={{
                            width: layout.queryWidth,
                            top: layout.queryTop,
                            left: layout.queryLeft,
                        }}
                    >
                    </input>                    
                    <button
                        className="query-button"
                        onClick={this.handleQuerySubmit}
                        style={{
                            width: 80,
                            top: layout.queryTop,
                            left: layout.queryLeft + layout.queryWidth + 20,
                        }}
                    >Ask</button>
                </div>                
            </div>
        );
    }    
}

let bubblesInitialized = false;

class BubbleDeets{
    constructor(internalID,text,typetext,bubbles,parentBubbleId,closestMatchId,closestMatchText, xLocation, yLocation,bubsInConcept){ //last three are not set on construction
        let room = typetext;
        if(typetext == 'info-field' | typetext == 'info-value'){
            room = 'info'
        }
        if(typetext == 'concept'){
            room = 'work'
        }
        this.internalID = internalID;
        this.id = ((internalID == '') ? getNextBubbleID() : internalID);
        this.text = text;
        this.type = typetext;        
        this.bubbles = bubbles;
        this.parentBubbleId = parentBubbleId;
        this.room = room;
        this.closestMatchId = closestMatchId;
        this.closestMatchText = closestMatchText;
        this.shrink = false;
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
            this.yLocation = nextYLocation(this.type,this.id,this.parentBubbleId);
        }
    }
}

let nextBubbleID = 0;
function getNextBubbleID(){
    const next = nextBubbleID;
    nextBubbleID++;
    return next.toString();
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
const infoValueRows = 3;

function nextXLocation(type,id,parentId){
    if (type === 'subject' | type === 'condition'){
        return layout.BubbleLeftMargin;
    }else if (type === 'info-field'){
        // return layout.InfoBubbleLeft;
        return 0;
    }else if (type === 'info-value'){
        //console.log(((parseInt(id)-parseInt(parentId))%infoValueRows + 1)*105);
        // return layout.InfoBubbleLeft + 55 + (((parseInt(id)-parseInt(parentId)-1)%infoValueRows + 1)*105);
        return 55 + (((parseInt(id)-parseInt(parentId)-1)%infoValueRows + 1)*105);
    }else{
    return 300;
    }
}

function nextYLocation(type,id,parentId){
    //console.log(type);
    if (type === 'subject'){
        const nextY =  layout.BubbleTopMargin + subjectCount*60;
        subjectCount++;
        return nextY;
    }
    else if (type === 'condition'){
        const nextY = layout.conditionBubbleTopMargin + conditionCount*60;
        conditionCount++;
        return nextY;
    }
    else if (type === 'info-field'){
        const nextY = layout.BubbleTopMargin + infoFieldCount*55;
        infoFieldCount++;
        return nextY;
    }
    else if (type === 'info-value'){
        const nextY = layout.BubbleTopMargin + (infoFieldCount-1)*55 + 5;
        if((parseInt(id)-parseInt(parentId)-1)%infoValueRows === 2){
            infoFieldCount++;
        }
        return nextY;
    }
    else{
        return 300;
    }    
}

export default Space;
