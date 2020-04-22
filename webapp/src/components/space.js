import React from 'react';
import Bubble from './bubble.js';
import Ghost from './ghost.js';
import {lastDragStart, layout, initializeLayout, randomSampleQuery, sendParseLambdaBootMessage, sendSaveConceptLambdaBootMessage} from './helpers.js';
//import bubblesPayload from '../sample-payloads/bubblesv3.json';
//import bubbleUpdatePayload from './sample-payloads/bubbleUpdatev1.json'
import axios from 'axios';
// import AudioRecorder from 'react-audio-recorder';
// import WebAudioRecorder from 'web-audio-recorder-js';
// import { RecordRTC, RecordRTCPromisesHandler, invokeSaveAsDialog, StereoAudioRecorder, WebAssemblyRecorder, MediaStreamRecorder} from 'recordrtc';
import { RecordRTC, RecordRTCPromisesHandler, invokeSaveAsDialog, StereoAudioRecorder} from 'recordrtc';
import Dropdown from 'react-dropdown';
import { Link } from "react-router-dom";

class Space extends React.Component{
    constructor(props){
        super(props);
        initializeLayout();
        this.state = {
            bubbles: [],
            sampleQuery: randomSampleQuery(),
            queryInput: '',
            queryResponseHTML: '',
            workspace: this.props.workspace,
            recording: false,
            recorder: null,
            dataIsLoaded: false
          };
      }

    componentDidMount(){
        this.resetAllAndInitialize(this.state.workspace); //This initializes Bubbles
        sendParseLambdaBootMessage(this.state.workspace);
        sendSaveConceptLambdaBootMessage(this.state.workspace);
        bubblesInitialized = true;
    }

    initializeBubbles(){
        this.getAllBubbles()
    }
    
    getAllBubbles = () => {
        console.log('Sending populate http call with query: ' + this.state.workspace)
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/populate', {
            workspace: this.state.workspace,
            getItems: 'all'
        },
        )
        .then(function(response){
            console.log('populate http successful')
            //console.log(response)
            self.updateBubbles(response.data)
            self.deleteMissingConceptBubbles()
            self.formatConceptBubbles()
            self.setState({
                dataIsLoaded: true
            })
            console.log('got here')
        })
        .catch(function(error){
            console.log('populate http error')
            console.log(error);
        });
    }
    
    deleteMissingConceptBubbles = () => {
        let newBubbles = this.state.bubbles.slice(0);
        let bubble;
        for (bubble in newBubbles){
            if (newBubbles[bubble].type === 'concept'){
                let conceptBubID;
                newBubbles[bubble].bubsInConcept = this.returnNewBubsInConcept(newBubbles[bubble].bubsInConcept)
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }
    
    returnNewBubsInConcept = (ids) => {
        let newIDarray = [];
        let id;
        for (id in ids){
            if (typeof this.getBubble(ids[id]) !== 'undefined'){
                newIDarray.push(ids[id]);
            }else{
                console.log("One of the bubbles in this list is missing from the bubble array.  The most likely culprit is that the IDs of the info-fields and info-values in this dataset were reset somehow.  Delete the concept and re-create it to not see this error")
            }
        }
        return newIDarray
    }
    
    saveConcept = (concept) => {
        console.log('Sending create/update save_concept http call with internal ID: ' + concept.internalID)
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/save-concept', {
            internal_ID: concept.internalID,
            workspace: this.state.workspace,
            text: concept.text,
            concept_item_detail: this.getBubblesForAPI(concept.bubsInConcept),
            concept_items: concept.bubsInConcept,
            useHyponymNames: true
        },
        )
        .then(function(response){
            console.log('save_concept http successful')
            console.log(response);
            self.updateInternalID(concept.id,response['data']['conceptID']);
            self.updateText(concept.id, response['data']['conceptName']);
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
            concept_item_detail: '',
            concept_items: '',
            useHyponymNames: false
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
    
    getPresignedUrl = (blob) => {
        console.log('Sending call for presigned url to transcribe API')
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/transcribe', {
            option: 'geturl',
            workspace: this.state.workspace,
            filename: '',
            jobName: ''
        },
        )
        .then(function(response){
            console.log('transcribe get presigned url http successful');
            console.log(response);
            let presignedUrl = response.data.presignedurl;
            let fileName = response.data.fileName;
            self.uploadBlob(blob,presignedUrl,fileName);
        })
        .catch(function(error){
            console.log('transcribe get presigned url http error');
            console.log(error);
        });
    }
    
    uploadBlob = (blob, presignedUrl, fileName) => {
        console.log('Uploading File to S3')
        // invokeSaveAsDialog(blob,fileName); //uncomment for save file dialog
        var self = this;
        fetch(presignedUrl, {method: "PUT", body: blob, headers: {
            'Content-Type': 'audio/wav',
        }})
        .then((response) => {
            console.log('fetch upload file http response');
            console.log(response);
            self.startTranscription(fileName);
        });
    };
    
    startTranscription = (fileName) => {
        console.log('Sending call for transcription to start transcribing')
        var self = this;
        
        const responseWaitingText = '<p>Transcribing your question...</p>';

        this.setState({
            queryResponseHTML: responseWaitingText,                
        })
        
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/transcribe', {
            option: 'starttranscription',
            workspace: this.state.workspace,
            filename: fileName,
            jobName: ''
        },
        )
        .then(function(response){
            console.log('transcribe start transcription http successful');
            console.log(response);
            let jobName = response.data.jobName;
            console.log('transcription job name: ' + jobName);
            self.checkTranscription(jobName)
        })
        .catch(function(error){
            console.log('transcribe start transcription http error');
            console.log(error);
        });
    }
    
    checkTranscription = (jobName) =>{
        console.log('Sending call for transcription to check and see if it is done')
        var self = this;
        
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/transcribe', {
            option: 'checktranscription',
            workspace: this.state.workspace,
            filename: '',
            jobName: jobName
        },
        )
        .then(function(response){
            console.log('transcribe check transcription http successful');
            console.log(response);
            let isReady = response.data.isReady;
            console.log('Is transcription ready: ' + isReady);
            if(isReady){
                let transcription = response.data.transcription
                self.setTranscriptAndSubmit(transcription).bind(self);
            }else{
                self.callCheckTranscription(jobName);
            }
        })
        .catch(function(error){
            console.log('transcribe check transcription http error');
            console.log(error);
        });
    }
    
    async callCheckTranscription(jobName){
        await new Promise(r => setTimeout(r, 5000));
        this.checkTranscription(jobName)
    }
    
    async setTranscriptAndSubmit(transcription){
        this.setState({
            queryInput: transcription,                
        })
        await new Promise(r => setTimeout(r, 10)); // We have to add this delay because using setState's callback is not working
        this.handleQuerySubmit() 
    }
    
    handleQuerySubmit = () => {
        console.log('Sending parse http call with query: ' + this.state.queryInput)
        var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/parse', {
            query: this.state.queryInput,
            workspace: this.state.workspace
        },
        )
        .then(function(response){
            console.log('http successful')
            console.log(response)
            if ('errorMessage' in response.data){
                console.log('error from parse query')
                self.setState({
                    queryResponseHTML: '<p>There was an error answering this question.. Oops!</p>',                
                })
            }else{
                self.updateBubbles(response.data)
                self.updateQueryResponse(response.data)
            }
        })
        .catch(function(error){
            console.log('http error')
            console.log(error);
        });
        window.setTimeout(this.detectLambdaBoot,1200);
        const responseWaitingText = '<p>...</p>';

        this.setState({
            queryResponseHTML: responseWaitingText,                
        })
    }
    
    formatConceptBubbles(){
        let newBubbles = this.state.bubbles;
        let bubble;
        for (bubble in newBubbles){
            if (newBubbles[bubble].type === 'concept'){
                this.updateRoom(newBubbles[bubble].id, 'concept');
                this.updateShrink(newBubbles[bubble].id, true);
                let conceptBubID;
                for (conceptBubID in newBubbles[bubble].bubsInConcept){
                    this.updateRoom(newBubbles[bubble].bubsInConcept[conceptBubID], 'concept');
                    this.updateShrink(newBubbles[bubble].bubsInConcept[conceptBubID], true);
                }
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }

    createBubbleDeets(bubbles){
        const newBubbles = bubbles.map((bub) => {
            const newBub = new BubbleDeets(bub.internalID, bub.name, bub.type, bub.parent_field_id, bub.parent_field_name, "", bub.closestMatchId,bub.closestMatchText, "", "", bub.concept_items, true, bub.field_rank, bub.value_rank, bub.data_type, bub.sample_1, bub.sample_2, bub.sample_3);
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
            this.createConcept(dragged,dropped,e)
            // this.positionConceptBubbles(newConcept,newConcept.xLocation,newConcept.yLocation)
        }
    }

    getBubble = (id) => {
        // const flatBubs = this.bubbleFlattener(this.state.bubbles);
        let flatBubs = this.state.bubbles.slice(0)
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

        const newConcept = new BubbleDeets('','Concept','concept','','','','','',newX,newY,newbubsInConcept,false)
        newBubbles.unshift(newConcept);
        this.saveConcept(newConcept);
        // console.log(newBubbles);
        this.setState({   // Have to refactor everywhere now since i am actually setting state directly by assigning an array to the state array
            bubbles: newBubbles
        }, this.positionConceptBubbles(newConcept,newX,newY))  //we need to pass positionConceptBubbles as a callback since setState is Async
    }

    addToConcept = (draggedChild,droppedConcept, e) => {
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
        // console.log('Removing from Concept: ' + childID)
        let newBubbles = this.state.bubbles;
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].type === 'concept'){
                for (let iter2 = 0; iter2 < newBubbles[iter].bubsInConcept.length; iter2++){
                    // console.log("Length of bubsInConcept: " + newBubbles[iter].bubsInConcept.length)
                    if (newBubbles[iter].bubsInConcept[iter2] === childID){
                        newBubbles[iter].bubsInConcept.splice(iter2,1);
                        //now removing concept if it contains no bubs:
                        if(newBubbles[iter].bubsInConcept.length === 0){
                            this.saveDeleteConcept(newBubbles[iter]);
                            newBubbles.splice(iter,1);
                            break;
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
        // console.log('Successfully Removed from Concept: ' + childID)
    }

    removeBubble = (bubbleToRemove) => {  //TODO Delete this?
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
        this.updateLastDraggedRoom('work');
        this.updateLastDraggedShrink(false);
        this.moveBubble(e);
        this.removeFromConcept(lastDragStart.id.toString());
        // console.log(this.state.bubbles);
    }
    
    handleConceptRoomDrop(e){
        const draggedID = lastDragStart.id.toString();
        const draggedType = this.getBubble(draggedID).type;
        if (draggedType === 'concept'){
            this.updateLastDraggedRoom('concept');
            this.updateLastDraggedShrink(true);
            this.moveBubble(e);
        }
    }
    
    handleSubjectRoomDrop(e){
        const draggedID = lastDragStart.id.toString();
        const draggedType = this.getBubble(draggedID).type;
        if (draggedType === 'subject'){
            this.updateLastDraggedRoom('subject');
            this.removeFromConcept(lastDragStart.id.toString());
        }
    }
    
    handleConditionRoomDrop(e){
        const draggedID = lastDragStart.id.toString();
        const draggedType = this.getBubble(draggedID).type;
        if (draggedType === 'condition'){
            this.updateLastDraggedRoom('condition');
            this.removeFromConcept(lastDragStart.id.toString());
        }
    }
    
    handleInfoRoomDrop(e){
        const draggedID = lastDragStart.id.toString();
        const draggedType = this.getBubble(draggedID).type;
        if (draggedType === 'info-field' | draggedType === 'info-value'){
            this.updateLastDraggedRoom('info');
            this.updateLocation(draggedID,draggedType);
            this.removeFromConcept(lastDragStart.id.toString());
        }
    }
    
    updateLocation(id, type){
        const fieldRank = this.getBubble(id).fieldRank;
        const valueRank = this.getBubble(id).valueRank;
        let newBubbles = this.state.bubbles.slice(0);
        let topBubble;
        for (topBubble in newBubbles){
            if (newBubbles[topBubble].id === id){
                newBubbles[topBubble].xLocation = getXLocation(type,fieldRank,valueRank);
                newBubbles[topBubble].yLocation = getYLocation(type,fieldRank,valueRank);
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }
    
    handleInputKeyPress = (e) => {
        let code = e.keyCode || e.which;
        if(code === 13) { //13 is the enter keycode
            this.handleQuerySubmit()
        } 
    }

    updateLastDraggedRoom(roomValue){
        const draggedID = lastDragStart.id.toString();
        this.updateRoom(draggedID,roomValue);
    }
    
    updateRoom(id,roomValue){
        let newBubbles = this.state.bubbles.slice(0);
        let topBubble;
        for (topBubble in newBubbles){
            if (newBubbles[topBubble].id === id){
                newBubbles[topBubble].room = roomValue;
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }
    
    updateText(id,textValue){
        let newBubbles = this.state.bubbles.slice(0);
        let bubble;
        for (bubble in newBubbles){
            if (newBubbles[bubble].id === id){
                newBubbles[bubble].text = textValue;
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }
    
    updateLastDraggedShrink(shrinkValue){
        const draggedID = lastDragStart.id.toString();
        this.updateShrink(draggedID,shrinkValue)
    }
    
    updateShrink(id,shrinkValue){
        let newBubbles = this.state.bubbles.slice(0);
        for (let iter = 0; iter < newBubbles.length; iter++){
            if (newBubbles[iter].id === id){
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
                newBubbles[iter].id = internalID;
            }
        }
        this.setState({
            bubbles: newBubbles
        })
    }

    moveBubble(e){
        //console.log('workroom drop, id of dragged bubble is: ' + lastDragStart.id);
        const newX = e.nativeEvent.clientX - lastDragStart.shiftX ; //I don't know why subtracting 3 pixels is necessary but it is to get the shift perfect
        const newY = e.nativeEvent.clientY - lastDragStart.shiftY ; //SOLVED: I had a 3 px margin in my main bubble css class!

        const newBubbles = this.state.bubbles.map((bub) => {
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
    
    async handleRecord(){
        if (this.hasGetUserMedia()) {
            if (!this.state.recording){
                let stream = await navigator.mediaDevices.getUserMedia({video: false, audio: true});
                let recorder = new RecordRTCPromisesHandler(stream, {
                    type: 'audio',
                    // recorderType: MediaStreamRecorder,
                    recorderType: StereoAudioRecorder,
                    mimeType: 'audio/wav',
                });
                recorder.startRecording();
                
                this.setState({
                    recording: true,
                    recorder: recorder,
                })
            }else{
                await this.state.recorder.stopRecording();
                let blob = await this.state.recorder.getBlob();
                
                // var ffmpeg = require('ffmpeg')
                this.getPresignedUrl(blob);  //This triggers a series of calls to get a signed url, upload the blob there, and trigger the transcription
                
                this.setState({
                    recording: false,
                    recorder: null,
                })
            }
        } else {
            alert('getUserMedia() is not supported by your browser');
        }
    }
    
    hasGetUserMedia() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }
    
    handleWorkspaceSelect = (e) =>{
        this.resetAllAndInitialize(e.value);
    }
    
    resetAllAndInitialize = (workspace) => {
        // console.log('props workspace is: ' + this.props.workspace)
        this.setState({
            workspace: workspace,
            bubbles: [],
            dataIsLoaded: false,
            queryInput: '',
            queryResponseHTML: ''
        },
        this.initializeBubbles //pass in function to get new workspace bubbles as a callback to resetting the state
        )
    }
    
    resetAll = (workspace) => {
        this.setState({
            workspace: workspace,
            bubbles: [],
            dataIsLoaded: false,
            queryInput: '',
            queryResponseHTML: ''
        });
    }

    detectLambdaBoot = () => {
        if(this.state.queryResponseHTML === '<p>...</p>'){
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
    
    getBubbles(ids){
        let bubbleArray = [];
        let id;
        for (id in ids){
            bubbleArray.push(this.getBubble(ids[id]));
        }
        return bubbleArray
    }
    
    getBubblesForAPI(ids){
        let bubbleArray = [];
        let apiArray = [];
        let id;
        for (id in ids){
            bubbleArray.push(this.getBubble(ids[id]));
        }
        let bubble;
        for (bubble in bubbleArray){
            let newItem = {
                'text': bubbleArray[bubble].text,
                'query_part': bubbleArray[bubble].type,
                'item_id': bubbleArray[bubble].internalID,
                'closest_match_text': bubbleArray[bubble].closestMatchText,
                'closest_match_id': bubbleArray[bubble].closestMatchId
            }
            apiArray.push(newItem)
        }
        console.log(apiArray);
        return apiArray
    }

    renderBubble(bub){
        const conceptBubbles = this.getBubbles(bub.bubsInConcept)
        const dataIsLoaded = this.state.dataIsLoaded
        let parentFieldName = bub.parentFieldName
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
                  dataIsLoaded={dataIsLoaded}
                  parentFieldName={parentFieldName}
            />
        );
    }
    
    renderInfoGhost(bub){
        let parentFieldName = bub.parentFieldName
        let staticXLocation = getXLocation(bub.type,bub.fieldRank,bub.valueRank);
        let staticYLocation = getYLocation(bub.type,bub.fieldRank,bub.valueRank);
        
        return (
            <Ghost key={bub.id + 'ghost'}
                id= {bub.id}
                name= {bub.text}
                type= {bub.type}
                xLocation= {staticXLocation}
                yLocation= {staticYLocation}
                parentFieldName={parentFieldName}
                room='info'
                ghostType = {bub.type}
            />
        );
    }
    
    renderInfoDataType(bub){
        let parentFieldName = bub.parentFieldName
        let staticXLocation = getXLocation(bub.type,bub.fieldRank,bub.valueRank);
        let staticYLocation = getYLocation(bub.type,bub.fieldRank,bub.valueRank) + layout.bubbleHeight['info-field'] + layout.infoSpacing;
        
        return (
            <Ghost key={bub.id + 'type'}
                id= {bub.id}
                name= {bub.data_type}
                type= 'info-value'
                xLocation= {staticXLocation}
                yLocation= {staticYLocation}
                parentFieldName={parentFieldName}
                room='info'
                ghostType = 'data-type'
            />
        );
    }
    
    renderInfoSamples(bub){
        let parentFieldName = bub.parentFieldName
        let staticXLocation = getXLocation(bub.type,bub.fieldRank,bub.valueRank);
        let YLocation1 = getYLocation(bub.type,bub.fieldRank,bub.valueRank) + layout.bubbleHeight['info-field'] + layout.bubbleHeight['data-type'] + layout.infoSpacing * 2;
        let YLocation2 = getYLocation(bub.type,bub.fieldRank,bub.valueRank) + layout.bubbleHeight['info-field'] + layout.bubbleHeight['data-type'] + layout.bubbleHeight['data-sample'] + layout.infoSpacing * 2;
        let YLocation3 = getYLocation(bub.type,bub.fieldRank,bub.valueRank) + layout.bubbleHeight['info-field'] + layout.bubbleHeight['data-type'] + layout.bubbleHeight['data-sample'] * 2 + layout.infoSpacing * 2;
        
        return (
            <div>
                <Ghost key={bub.id + 'sample_1'}
                    id= {bub.id}
                    name= {bub.sample_1}
                    type= 'info-value'
                    xLocation= {staticXLocation}
                    yLocation= {YLocation1}
                    parentFieldName={parentFieldName}
                    room='info'
                    ghostType = 'data-sample'
                />
                <Ghost key={bub.id + 'sample_2'}
                    id= {bub.id}
                    name= {bub.sample_2}
                    type= 'info-value'
                    xLocation= {staticXLocation}
                    yLocation= {YLocation2}
                    parentFieldName={parentFieldName}
                    room='info'
                    ghostType = 'data-sample'
                />
                <Ghost key={bub.id + 'sample_3'}
                    id= {bub.id}
                    name= {bub.sample_3}
                    type= 'info-value'
                    xLocation= {staticXLocation}
                    yLocation= {YLocation3}
                    parentFieldName={parentFieldName}
                    room='info'
                    ghostType = 'data-sample'
                />
            </div>
        );
    }


    render(){
        if (!bubblesInitialized){
            return<div className = "space"></div>; //doing this so that render doesn't execute before bubbles are initialized on componentdidmount
        }

        let workRoomBubbleArray = [];
        let workRoomConceptArray = [];
        let subjectRoomBubbleArray = [];
        let conditionRoomBubbleArray = [];
        let infoRoomBubbleArray = [];
        let conceptRoomBubbleArray = [];
        
        let flatBubbles = this.state.bubbles.slice(0) //Loop through and render all bubble lists by room
        for (let bubblePos = 0; bubblePos < flatBubbles.length; bubblePos++){
            if (flatBubbles[bubblePos].room === 'work')
                if (flatBubbles[bubblePos].type === 'concept'){
                    workRoomConceptArray.push(this.renderBubble(flatBubbles[bubblePos]));
                }else{
                    workRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos]));
                }
            if (flatBubbles[bubblePos].room === 'subject')
                subjectRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos]));   
            if (flatBubbles[bubblePos].room === 'condition')
                conditionRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos])); 
            if (flatBubbles[bubblePos].room === 'info')
                infoRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos])); 
            if (flatBubbles[bubblePos].room === 'concept')
                if (flatBubbles[bubblePos].type === 'concept'){
                    conceptRoomBubbleArray.push(this.renderBubble(flatBubbles[bubblePos])); 
                }
        };
        
        let fieldGhostArray = [];
        
        for (let bubblePos = 0; bubblePos < flatBubbles.length; bubblePos++){
            if (flatBubbles[bubblePos].type === 'info-field'){
                fieldGhostArray.push(this.renderInfoGhost(flatBubbles[bubblePos]));
                fieldGhostArray.push(this.renderInfoDataType(flatBubbles[bubblePos]));
                fieldGhostArray.push(this.renderInfoSamples(flatBubbles[bubblePos]));
            }else if (flatBubbles[bubblePos].type === 'info-value'){
                fieldGhostArray.push(this.renderInfoGhost(flatBubbles[bubblePos]))
            }
            //create other arrays
        };
        
        let recordText = (this.state.recording ? '🔴' : '🎤');
        let workspaces = [];
        let workspaceDropdownDisablingClass = (this.state.dataIsLoaded ? 'query-workspace-dropdown' : 'query-workspace-dropdown-disable')
        let workspaceDefault = (this.state.dataIsLoaded ? this.state.workspace : 'Loading: ' + this.state.workspace + '...');
        
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
                >
                </div>                
                <div className = "room subject-room"
                    onDrop={this.handleSubjectRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        width: layout.lexWidth,
                        top: layout.lexTop,
                        bottom: layout.bottomMargin,
                        left: layout.leftMargin,
                    }}
                    >
                    New Subjects
                    {subjectRoomBubbleArray.reverse()}
                </div>
                <div className = "room condition-room"
                    onDrop={this.handleConditionRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        width: layout.lexWidth,
                        bottom: layout.bottomMargin,
                        top: layout.lexTop,
                        left: layout.conditionLeft,
                    }}
                    >
                    New Conditions
                    {conditionRoomBubbleArray.reverse()}
                </div>
                <div className = "room info-room"
                    onDrop={this.handleInfoRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        left: layout.leftMargin,
                        top: layout.topMargin,
                        right: layout.rightMargin,
                        height: layout.infoHeight,
                    }}
                    >
                    {fieldGhostArray}
                    {infoRoomBubbleArray}
                </div>
                <div className = "room concept-room"
                    onDrop={this.handleConceptRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        top: layout.lexTop,
                        bottom: layout.bottomMargin,
                        right: layout.rightMargin,
                        width: layout.conceptWidth,
                    }}
                    >
                    Concept Storage
                    {conceptRoomBubbleArray}
                </div>
                {workRoomConceptArray}
                {workRoomBubbleArray}
                <div className = "query"
                    >
                    <Link to="/">
                        <button 
                            className="menu-button"
                            onClick={this.resetAll}
                            style={{
                                width: layout.homeWidth,
                                top: layout.queryTop,
                                left: layout.homeLeft,
                            }}
                        >Home</button>
                    </Link>
                    <input 
                        className="query-input"
                        type="text"
                        placeholder={this.state.sampleQuery} 
                        onChange={this.handleQueryChange}    
                        onKeyPress={this.handleInputKeyPress}
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
                    <button
                        className="query-audio-button"
                        onClick={this.handleRecord.bind(this)}
                        style={{
                            width: 35,
                            height: 23,
                            top: layout.queryTop,
                            left: layout.queryLeft + layout.queryWidth + 110,
                        }}
                    >{recordText}</button>
                    <button
                        className="query-workspace-dropdown-container"
                        style={{
                            width: layout.infoWidth,
                            height: 30,
                            top: layout.queryTop - 4,
                            right: layout.rightMargin,
                        }}
                        ><Dropdown 
                            className={workspaceDropdownDisablingClass}
                            options={workspaces}
                            onChange={this.handleWorkspaceSelect}
                            value={workspaceDefault}
                            placeholder="Workspace"
                        ></Dropdown>
                    </button>
                </div>                
            </div>
        );
    }    
}

let bubblesInitialized = false;

class BubbleDeets{
    constructor(internalID, text, typetext, parentFieldID, parentFieldName, parentFrontendID, closestMatchId, closestMatchText, xLocation, yLocation, bubsInConcept, fromServer, fieldRank, valueRank, data_type, sample_1, sample_2, sample_3){ //last three are not set on construction
        let room = typetext;
        let shrink = false;
        if(typetext === 'info-field' | typetext === 'info-value'){
            room = 'info';
        }
        if(typetext === 'concept'){
            room = 'work';
        }
        const frontendID = getNextBubbleID();
        this.internalID = internalID;
        this.frontendID = frontendID;
        this.id = ((internalID === '') ? frontendID : internalID);
        this.text = text;
        this.type = typetext;        
        // this.bubbles = bubbles;
        this.parentFieldID = parentFieldID;
        this.parentFieldName = parentFieldName;
        this.parentFrontendID = parentFrontendID;
        this.room = room;
        this.closestMatchId = closestMatchId;
        this.closestMatchText = closestMatchText;
        this.shrink = shrink;
        this.fieldRank = fieldRank;
        this.valueRank = valueRank;
        this.data_type = data_type;
        this.sample_1 = sample_1;
        this.sample_2 = sample_2;
        this.sample_3 = sample_3;
        if (bubsInConcept){
            this.bubsInConcept = bubsInConcept;
        }else{
            this.bubsInConcept = [];
        }
        if(xLocation){
            this.xLocation = xLocation;
        }else{
            this.xLocation = getXLocation(this.type,this.fieldRank,this.valueRank);
        }
        if(xLocation){
            this.yLocation = yLocation;
        }else{
            this.yLocation = getYLocation(this.type,this.fieldRank,this.valueRank);
        }
    }
}

let nextBubbleID = 0;
function getNextBubbleID(){
    const next = nextBubbleID;
    nextBubbleID++;
    return next.toString();
}

function getXLocation(type,fieldRank,valueRank){
    if (type === 'subject' | type === 'condition'){
        return layout.BubbleLeftMargin;
    }else if (type === 'info-field'){
        return fieldRank * (layout.bubbleWidth['info-field'] + layout.infoSpacing);
    }else if (type === 'info-value'){
        return fieldRank * (layout.bubbleWidth['info-field'] + layout.infoSpacing);
    }else{
    return 300;
    }
}

function getYLocation(type,fieldRank,valueRank){
    if (type === 'info-field'){
        return layout.infoSpacing;
    }
    else if (type === 'info-value'){
        const fieldHeightAdjustment = 0 - layout.bubbleHeight['info-value'] + layout.bubbleHeight['info-field'] + layout.infoSpacing
        const extraInfoSpacing = layout.bubbleHeight['data-type'] + layout.bubbleHeight['data-sample'] * 3 + layout.infoSpacing * 5
        return valueRank * (layout.bubbleHeight['info-value'] + layout.infoSpacing) + fieldHeightAdjustment + extraInfoSpacing
    }
    else{
        return 300;
    }    
}

export default Space;
