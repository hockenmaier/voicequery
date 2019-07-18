import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

var lastDragStartId = '';

class Bubble extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            dragover: false,
        };
    }
    
    handleDragOver(e){
        let dragover = true;
        //console.log('target id is: ' + e.nativeEvent.target.id + ' and this.props.id is: ' + this.props.id + ' and global lasdragstartid is: ' + lastDragStartId);
        
        if (e.nativeEvent.srcElement.id === lastDragStartId.toString()){
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
            <div>
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
            </div>
        );
    }
}


class Space extends React.Component{
    constructor(props){
        super(props);
        this.canvasRef = React.createRef();
        this.state = {
            bubbles: [
                {
                    id: "0",
                    text: "visitor",
                    type: "bubble subject",
                    xLocation: 50,
                    yLocation: 50
                },
                {
                    id: "1",
                    text: "costume",
                    type: "bubble subject",
                    xLocation: 50,
                    yLocation: 110
                },
                {
                    id: "2",
                    text: "people",
                    type: "bubble subject",
                    xLocation: 50,
                    yLocation: 170
                },
                {
                    id: "3",
                    text: "rented",
                    type: "bubble condition",
                    xLocation: 50,
                    yLocation: 400
                },
                {
                    id: "4",
                    text: "on the lot",
                    type: "bubble condition",
                    xLocation: 50,
                    yLocation: 460
                }
              ],
          };
      }

    componentDidMount(){
        //getting the canvas here
        this.resizeCanvas();
        window.addEventListener('resize', this.resizeCanvas.bind(this), false);
    }
    
    resizeCanvas() { //this resizes the canvas and is called when the window size changes
        //console.log('resized')
        const canvas = this.canvasRef.current;
        const SizeX = window.innerWidth*.8;
        const SizeY = window.innerHeight*.6;
        canvas.width = SizeX;
        canvas.height = SizeY;
    }

    handleDragStart(e, id){
        // console.log("draggin in Space");
        // console.log('react SyntheticEvent ==> ', e);
        // console.log('nativeEvent ==> ', e.nativeEvent); //<- gets native JS event
        // console.log('id is: ' + id);
        //this.context.lastDragStartId = id;
        lastDragStartId = id;
    }
    handleDrop(e, id){
        console.log('dropped, id is: ' + id);
    }

    handleCanvasDrop(e){
        console.log('canvas drop');
    }

    handleCanvasDragOver(e){
        console.log('canvas dragover');
    }

    render(){
        //createCanvas();
        //console.log(this.state.bubbles[0]);
        const bubbles = this.state.bubbles.map((bub) => {
            //console.log("id: " + bub.id + ' text: ' +bub.text+' type: ' +bub.type);
            return (
              <Bubble key={bub.id}
                    id= {bub.id}
                    name= {bub.text}
                    type= {bub.type}
                    onDragStart={(event) => this.handleDragStart(event, bub.id)} 
                    onDrop={(event) => this.handleDrop(event, bub.id)}
                    xLocation= {bub.xLocation}
                    yLocation={bub.yLocation}
                />
            );
        });
        
        
        return(
            <div className = "space">                
                <div className = "canvas"
                    ref={this.canvasRef} 
                    width={0} 
                    height={200} 
                    id="space_canvas"
                    onDrop={this.handleCanvasDrop}
                    onDragOver={this.handleCanvasDragOver}
                    style={{
                        position: "absolute",
                        height: '900px',
                        width: '900px',
                        top: '10px',
                        left: '10px',
                    }}
                    >
                </div>
                {bubbles}
            </div>
        );
    }    
}

ReactDOM.render(<Space />, document.getElementById('root'));
