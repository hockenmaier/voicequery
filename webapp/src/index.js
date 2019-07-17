import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

class Bubble extends React.Component{
    allowDrop(){
        console.log('bubble dragover: ' + this.props.id);
    }

    render(){
        return(
            <div>
                <button className = {this.props.type} 
                height = {200} 
                width = {150} 
                draggable="true" 
                onDragStart={this.props.onDrag}
                onDrop={this.props.onDrop}
                onDragOver={this.allowDrop.bind(this)}
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
        const canvas = this.canvasRef.current;
        const ctx = canvas.getContext('2d');
        this.setState({
            canvas: canvas,
            ctx: ctx
        })
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

    handleDrag(event, id){
        console.log("draggin in Space");
        console.log('react SyntheticEvent ==> ', event);
        console.log('nativeEvent ==> ', event.nativeEvent); //<- gets native JS event
        console.log('id is: ' + id);
    }
    handleDrop(event, id){
        console.log('dropped, id is: ' + id);
    }

    handleCanvasDrop(event){
        console.log('canvas drop');
    }

    handleCanvasDragOver(event){
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
                    type= {'subject'}
                    onDrag={(event) => this.handleDrag(event, 0)} 
                    onDrop={(event) => this.handleDrop(event, 0)} 
                />
                <Bubble
                    id= {1}
                    name= {'On the Lot'}
                    type= {'condition'}
                    onDrag={(event) => this.handleDrag(event, 1)}
                    onDrop={(event) => this.handleDrop(event, 1)} 
                />
            </div>
        );
    }    
}

ReactDOM.render(<Space />, document.getElementById('root'));
