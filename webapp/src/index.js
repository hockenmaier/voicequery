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
        let bubbleHeight = (this.state.dragover ? '73px' : '65px');
        let bubbleWidth = (this.state.dragover ? '160px' : '150px');
        return(
            <div className = 'bubble'>
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
                        width: bubbleWidth
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
      }

    componentDidMount(){
        //getting the canvas here
        this.resizeCanvas();
        window.addEventListener('resize', this.resizeCanvas.bind(this), false);
    }
    
    resizeCanvas() { //this resizes the canvas and is called when the window size changes
        console.log('resized')
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
        return(
            <div className = "space">                
                <div className = "canvas">
                    <canvas ref={this.canvasRef} 
                    width={0} 
                    height={0} 
                    id="space_canvas"
                    onDrop={this.handleCanvasDrop}
                    onDragOver={this.handleCanvasDragOver}
                    >Please update your browser to use this app
                    </canvas>
                </div>
                <Bubble
                    id= {0}
                    name= {'Costume'}
                    type= {'bubble subject'}
                    onDragStart={(event) => this.handleDragStart(event, 0)} 
                    onDrop={(event) => this.handleDrop(event, 0)} 
                />
                <Bubble
                    id= {1}
                    name= {'On the Lot'}
                    type= {'bubble condition'}
                    onDragStart={(event) => this.handleDragStart(event, 1)}
                    onDrop={(event) => this.handleDrop(event, 1)} 
                />
            </div>
        );
    }    
}

ReactDOM.render(<Space />, document.getElementById('root'));
