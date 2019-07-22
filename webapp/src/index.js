import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

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
}

let bubblesInitialized = false;

//var lastDragStartId = '';
class lastDragStart{
    id = '';
    shiftX = 0;
    shifty = 0;
}

class BubbleDeets{
    constructor(internalId,text,typetext,bubbles,parentBubbleId){
        this.internalID = internalId;
        this.id = getNextBubbleID();
        this.text = text;
        this.type ='bubble ' + typetext;
        this.xLocation = nextXLocation(this.type);
        this.yLocation = nextYLocation(this.type);
        this.bubbles = bubbles;
        this.parentBubbleId = parentBubbleId;
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
            width = 120
        }else if (this.props.type === 'bubble info-field'){
            height = 40;
            width = 150
        }
        else if (this.props.type === 'bubble info-value'){
            height = 30;
            width = 120
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
        initializeLayout();
        this.state = {
            bubbles: [                
                    // new BubbleDeets("","visitor", "subject"),
                    // new BubbleDeets("","through gate 6", "condition"),    
                    // new BubbleDeets("","costume", "subject"),          
                    // new BubbleDeets("","people", "subject"),   
                    // new BubbleDeets("","rented", "condition"),    
                    // new BubbleDeets("","on the lot", "condition"),
                    // new BubbleDeets("","ladder light", "subject"),
                    // new BubbleDeets("","transaction_id", "info-field"),
                    // new BubbleDeets("","checkout_date", "info-field"),
                    // new BubbleDeets("","checkin_date", "info-field"),                    
                    // new BubbleDeets("","transaction_type", "info-field"),
                    // new BubbleDeets("","last_update_date", "info-field"),
                    // new BubbleDeets("","asset_id", "info-field"),
                    // new BubbleDeets("","asset_name", "info-field"),
                    // new BubbleDeets("","asset_department", "info-field"),
                    // new BubbleDeets("","order_id", "info-field"),
                    {
                        internalID: "",
                        name: "visitor",
                        type: "subject",
                        bubbles: []
                    },                    
                    {
                        internalID: "",
                        name: "through gate 6",
                        type: "condition",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "costume",
                        type: "subject",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "people",
                        type: "subject",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "rented",
                        type: "condition",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "on the lot",
                        type: "condition",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "ladder light",
                        type: "subject",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "transaction_id",
                        type: "info-field",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "checkout_date",
                        type: "info-field",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "checkin_date",
                        type: "info-field",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "transaction_type",
                        type: "info-field",
                        bubbles: [
                            {
                                internalID: "",
                                name: "rental",
                                type: "info-value",
                                bubbles: []
                            },
                            {
                                internalID: "",
                                name: "sale",
                                type: "info-value",
                                bubbles: []
                            },
                            {
                                internalID: "",
                                name: "subrental",
                                type: "info-value",
                                bubbles: []
                            }
                        ]
                    },
                    {
                        internalID: "",
                        name: "last_update_date",
                        type: "info-field",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "asset_id",
                        type: "info-field",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "asset_name",
                        type: "info-field",
                        bubbles: []
                    },
                    {
                        internalID: "",
                        name: "asset_department",
                        type: "info-field",
                        bubbles: []
                    },
              ],
            sampleQuery: randomSampleQuery(),
            queryInput: '',
          };
        this.handleQueryChange = this.handleQueryChange.bind(this);
      }

    componentDidMount(){
        this.initializeBubbles(this.state.bubbles);
        bubblesInitialized = true;
    }

    initializeBubbles(bubbles){
        //console.log(this.state.bubbles);
        const newBubbles = bubbles.map((bub) => {
            const newBub = new BubbleDeets(bub.internalID,bub.name,bub.type,bub.bubbles,"");
            if(newBub.bubbles.length > 0){
                //console.log("internal bubbles are: " + newBub.bubbles);
                //console.log(newBub.bubbles);
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
        //console.log(newBubbles);
    }

    handleBubbleDragStart(e, id){
        lastDragStart.id = id;
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
        const newX = e.nativeEvent.clientX - lastDragStart.shiftX -3; //I don't know why subtracting 3 pixels is necessary but it is to get the shift perfect
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
        //console.log(this.state.bubbles[0]);
        //console.log(this.state.bubbles);
        let bubbleArray = [];
        let bubbles = this.state.bubbles;
        //console.log(bubbles);
        let outer;
        for (outer = 0; outer < bubbles.length; outer++){
            //console.log("id: " + bub.id + ' text: ' +bub.text+' type: ' +bub.type);
            
            if (bubbles[outer].bubbles.length > 0){
                //console.log(bubbles[outer].bubbles);
                let inner;
                for (inner = 0; inner < bubbles[outer].bubbles.length; inner++){
                    bubbleArray.push(this.renderBubble(bubbles[outer].bubbles[inner]));
                }
                // bub.bubbles.forEach(function(intBub){
                //     bubbleArray.push(this.renderBubble(intBub));
                // });
            }
            bubbleArray.push(this.renderBubble(bubbles[outer]));            
        };
        
        return(
            <div className = "space">                
                <div className = "work-room"
                    //ref={this.canvasRef} 
                    //id="space_canvas"
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
                    Available Info - rental_transaction Table
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

function nextXLocation(type){
    if (type === 'bubble subject' | type === 'bubble condition'){
        return layout.BubbleLeftMargin;
    }else if (type === 'bubble info-field'| type === 'bubble info-value'){
        return layout.InfoBubbleLeft;
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
    else if (type === 'bubble info-field'| type === 'bubble info-value'){
        const nextY = layout.BubbleTopMargin + infoFieldCount*55;
        infoFieldCount++;
        return nextY;
    }
    else{
        return 10;
    }
    
}

ReactDOM.render(<Space />, document.getElementById('root'));
