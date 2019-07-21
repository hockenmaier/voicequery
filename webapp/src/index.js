import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

//var lastDragStartId = '';
class lastDragStart{
    id = '';
    shiftX = 0;
    shifty = 0;
}

class BubbleDeets{
    constructor(internalId,text,typetext){
        this.internalID = internalId;
        this.id = getNextBubbleID();
        this.text=text;
        this.type='bubble ' + typetext;
        this.xLocation= nextXLocation(this.type);
        this.yLocation= nextYLocation(this.type);
    }
    id= "";
    text= "";
    type= "";
    xLocation= 0;
    yLocation= 0;
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
        let height = 50;
        let width = 120

        //modify size based on dragover event
        const dragScale = 1.2;
        height = (this.state.dragover ? height*dragScale : height);
        width = (this.state.dragover ? width*dragScale : width);
        
        //turn size into strings
        const stringHeight = (height + 'px');
        const stringWidth = (width + 'px');

        //set base location based on props
        const xLocation = this.props.xLocation;
        const yLocation = this.props.yLocation;

        //turn location into strings
        const stringXLocation = xLocation + 'px';
        const stringYLocation = yLocation + 'px';
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
                    left: stringXLocation
                }}
            >{this.props.name}
            </button>
        );
    }
}


class Space extends React.Component{
    constructor(props){
        super(props);
        this.canvasRef = React.createRef();
        this.state = {
            bubbles: [                
                    new BubbleDeets("","visitor", "subject"),
                    new BubbleDeets("","through gate 6", "condition"),    
                    new BubbleDeets("","costume", "subject"),          
                    new BubbleDeets("","people", "subject"),   
                    new BubbleDeets("","rented", "condition"),    
                    new BubbleDeets("","on the lot", "condition"),
                    new BubbleDeets("","ladder light", "subject"),
                    new BubbleDeets("","transaction_id", "info-field"),
                    new BubbleDeets("","checkout_date", "info-field"),
                    new BubbleDeets("","checkin_date", "info-field"),                    
                    new BubbleDeets("","transaction_type", "info-field"),
                    new BubbleDeets("","last_update_date", "info-field"),
                    new BubbleDeets("","asset_id", "info-field"),
                    new BubbleDeets("","asset_name", "info-field"),
                    new BubbleDeets("","order_id", "info-field"),
              ],
            sampleQuery: randomSampleQuery(),
            queryInput: '',
          };
        this.handleQueryChange = this.handleQueryChange.bind(this);
      }

    handleBubbleDragStart(e, id){
        // console.log("draggin in Space");
        // console.log('react SyntheticEvent ==> ', e);
        // console.log('nativeEvent ==> ', e.nativeEvent); //<- gets native JS event
        //console.log('id is: ' + id);
        lastDragStart.id = id;
        //console.log(e.nativeEvent);
        lastDragStart.shiftX = e.nativeEvent.clientX - e.nativeEvent.srcElement.getBoundingClientRect().left;
        lastDragStart.shiftY = e.nativeEvent.clientY - e.nativeEvent.srcElement.getBoundingClientRect().top;
    }
    handleBubbleDrop(e, id){
        e.nativeEvent.preventDefault();
        if (id === lastDragStart.id.toString()){
            this.moveBubble(e);
        }
        //console.log('bubble dropped upon, id of receiving bubble is: ' + id + ' and id of dragged bubble is: ' + lastDragStart.id);
    }

    handleWorkRoomDrop(e){
        this.moveBubble(e);
    }

    moveBubble(e){
        //console.log('workroom drop, id of dragged bubble is: ' + lastDragStart.id);
        //console.log(e.nativeEvent);        
        const newX = e.nativeEvent.clientX - lastDragStart.shiftX -3;
        const newY = e.nativeEvent.clientY - lastDragStart.shiftY -3;
        const newBubbles = this.state.bubbles.map((bub) => {
            //console.log("id: " + bub.id + ' text: ' +bub.text+' type: ' +bub.type);
            if (bub.id === lastDragStart.id.toString()){
                bub.xLocation = newX;
                //console.log('id is: ' + bub.id + ' and new x location is: '+ bub.xLocation);
                bub.yLocation = newY;
            }
            return bub;
        })
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

    render(){
        //createCanvas();
        //console.log(this.state.bubbles[0]);
        //console.log(this.state.bubbles);
        const bubbles = this.state.bubbles.map((bub) => {
            //console.log(bub.bub);
            //console.log("id: " + bub.id + ' text: ' +bub.text+' type: ' +bub.type);
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
        });        
        
        return(
            <div className = "space">                
                <div className = "work-room"
                    //ref={this.canvasRef} 
                    //id="space_canvas"
                    onDrop={this.handleWorkRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        position: "absolute",
                        height: window.innerHeight,
                        width: window.innerWidth,
                        top: '0px',
                        left: '0px',
                    }}
                    >
                </div>
                <div className = "top-bar"
                    style={{
                        top: '0px',
                        left: '0px',
                        height: '70px',
                        width: window.innerWidth,
                        }}
                ></div>                
                <div className = "subject-room"
                    style={{
                        height: '300px',
                        width: '300px',
                        top: '100px',
                        left: '30px',
                    }}
                    >
                    Unmapped Subjects
                </div>
                <div className = "condition-room"
                    style={{
                        height: '300px',
                        width: '300px',
                        top: '430px',
                        left: '30px',
                    }}
                    >
                    Unmapped Conditions
                </div>
                <div className = "info-room"
                    style={{
                        height: '630px',
                        width: '500px',
                        top: '100px',
                        right: '30px',
                    }}
                    >
                    Available Info - rental_transaction Table
                </div>
                {bubbles}
                <div className = "query"
                    style={{
                        height: '0px',
                        width: '0px',
                        top: '20px',
                        left: '30px',
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
    const randomInt = Math.floor(Math.random()*queries.length);
    //console.log(queries[randomInt]);
    return queries[randomInt];
}

let subjectCount = 0;
let conditionCount = 0;
let infoFieldCount = 0;

function nextXLocation(type){
    if (type === 'bubble subject' | type === 'bubble condition'){
        return 50;
    }else if (type === 'bubble info-field'){
        return window.innerWidth - 510;
    }
}

function nextYLocation(type){
    //console.log(type);
    if (type === 'bubble subject'){
        const nextY =  130 + subjectCount*60;
        subjectCount++;
        return nextY;
    }
    else if (type === 'bubble condition'){
        const nextY = 460 + conditionCount*60;
        conditionCount++;
        return nextY;
    }
    else if (type === 'bubble info-field'){
        const nextY = 130 + infoFieldCount*60;
        infoFieldCount++;
        return nextY;
    }
    else{
        return 10;
    }
    
}

ReactDOM.render(<Space />, document.getElementById('root'));
