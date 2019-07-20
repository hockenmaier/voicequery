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
    constructor(id,text,typetext){
        this.id = id;
        this.text=text;
        this.type=typetext;
        this.xLocation= nextXLocation(this.type);
        this.yLocation= nextYLocation(this.type);
    }
    id= "";
    text= "";
    type= "";
    xLocation= 0;
    yLocation= 0;
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
        let bubbleHeight = (this.state.dragover ? '57px' : '50px');
        let bubbleWidth = (this.state.dragover ? '130px' : '120px');
        const xLocationPixels = this.props.xLocation + 'px';
        const yLocationPixels = this.props.yLocation + 'px';

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
                    height: bubbleHeight,
                    width: bubbleWidth,
                    top: yLocationPixels,
                    left:xLocationPixels
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
                    new BubbleDeets("0","visitor", "bubble subject"),
                    new BubbleDeets("5","through gate 6", "bubble condition"),    
                    new BubbleDeets("1","costume", "bubble subject"),          
                    new BubbleDeets("2","people", "bubble subject"),   
                    new BubbleDeets("3","rented", "bubble condition"),    
                    new BubbleDeets("4","on the lot", "bubble condition"),
                    new BubbleDeets("6","ladder light", "bubble subject"),
              ],
          };
      }

    // componentDidMount(){
    //     //getting the canvas here
    //     this.resizeCanvas();
    //     window.addEventListener('resize', this.resizeCanvas.bind(this), false);
    // }
    
    // resizeCanvas() { //this resizes the canvas and is called when the window size changes
    //     //console.log('resized')
    //     const canvas = this.canvasRef.current;
    //     const SizeX = window.innerWidth*.8;
    //     const SizeY = window.innerHeight*.6;
    //     canvas.width = SizeX;
    //     canvas.height = SizeY;
    // }

    handleBubbleDragStart(e, id){
        // console.log("draggin in Space");
        // console.log('react SyntheticEvent ==> ', e);
        // console.log('nativeEvent ==> ', e.nativeEvent); //<- gets native JS event
        // console.log('id is: ' + id);
        //this.context.lastDragStartId = id;
        //console.log('drag started, id is: ' + id);
        //lastDragStartId = id;
        lastDragStart.id = id;
        //console.log(e.nativeEvent);
        lastDragStart.shiftX = e.nativeEvent.clientX - e.nativeEvent.srcElement.getBoundingClientRect().left;
        lastDragStart.shiftY = e.nativeEvent.clientY - e.nativeEvent.srcElement.getBoundingClientRect().top;
    }
    handleBubbleDrop(e, id){
        e.nativeEvent.preventDefault();
        //console.log('bubble dropped upon, id of receiving bubble is: ' + id + ' and id of dragged bubble is: ' + lastDragStart.id);
    }

    handleWorkRoomDrop(e){
        //console.log('workroom drop, id of dragged bubble is: ' + lastDragStart.id);
        //console.log(e.nativeEvent);
        const newX = e.nativeEvent.clientX - lastDragStart.shiftX -3;
        const newY = e.nativeEvent.clientY - lastDragStart.shiftY -3;
        //console.log(newX);
        const newBubbles = this.state.bubbles.map((bub) => {
            //console.log("id: " + bub.id + ' text: ' +bub.text+' type: ' +bub.type);
            if (bub.id === lastDragStart.id.toString()){
                bub.xLocation = newX;
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

    render(){
        //createCanvas();
        //console.log(this.state.bubbles[0]);
        //console.log(this.state.bubbles);
        const bubbles = this.state.bubbles.map((bub) => {
            //console.log(bub.bub);
            //console.log("id: " + bub.id + ' text: ' +bub.text+' type: ' +bub.type);
            return (
              <Bubble key={bub.id}
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
                <div className = "workroom"
                    //ref={this.canvasRef} 
                    //id="space_canvas"
                    onDrop={this.handleWorkRoomDrop.bind(this)}
                    onDragOver={this.handleWorkRoomDragOver}
                    style={{
                        position: "absolute",
                        height: '900px',
                        width: '1600px',
                        top: '0px',
                        left: '0px',
                    }}
                    >
                </div>
                <div className = "subjectroom"
                    style={{
                        height: '300px',
                        width: '300px',
                        top: '100px',
                        left: '40px',
                    }}
                    >
                    Unmapped Subjects
                </div>
                <div className = "conditionroom"
                    style={{
                        height: '300px',
                        width: '300px',
                        top: '430px',
                        left: '40px',
                    }}
                    >
                    Unmapped Conditions
                </div>
                {bubbles}
            </div>
        );
    }    
}

let subjectCount = 0;
let conditionCount = 0;

function nextXLocation(type){
    return 50;
}

function nextYLocation(type){
    console.log(type);
    if (type == 'bubble subject'){
        const nextY =  130 + subjectCount*60;
        subjectCount++;
        return nextY;
    }
    else if (type == 'bubble condition'){
        const nextY = 460 + conditionCount*60;
        conditionCount++;
        return nextY;
    }
    else{
        return 10;
    }
    
}

ReactDOM.render(<Space />, document.getElementById('root'));
