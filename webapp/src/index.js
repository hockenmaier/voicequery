import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

class Bubble extends React.Component{
    render(){  
        return(
            <div>
                <button className = {this.props.type} height = {200} width = {150}>{this.props.name}</button>
            </div>
        );
    }
}

class Space extends React.Component{
    constructor(props){
        super(props);
        this.canvasRef = React.createRef();
        this.state = {          
          canvas: document.getElementById('space_canvas'),
          ctx: null,
        };
        // console.log(ctx)
      }

    componentDidMount(){
        //creating the canvas here
        //const canvas = this.refs.canvas
        const canvas = this.canvasRef.current;
        //const mycanvas = React.createContext(canvas)
        const ctx = canvas.getContext('2d');
        this.setState({
            canvas: canvas,
            ctx: ctx
        })
        
        // console.log(canvas);
        // console.log(this.state.canvas);
        //console.log(this.context.mycanvas)
        // console.log(ctx);
        // console.log(this.state.ctx);
        // console.log(ctx)
        this.resizeCanvas();
        window.addEventListener('resize', this.resizeCanvas.bind(this), false);
    }
    
    resizeCanvas() { //this resizes the canvas and is called when the window size changes
        console.log('resized')
        // const canvas = this.refs.canvas
        const canvas = this.canvasRef.current;
        //const canvas = this.state.canvas;
        const SizeX = window.innerWidth*.9;
        const SizeY = window.innerHeight*.6;
        canvas.width = SizeX;
        canvas.height = SizeY;
    }

    // renderBubble(){
    //     //const canvas = this.refs.canvas
    //     //const ctx = canvas.getContext('2d');
    //     console.log("rendering bubble")
    //     const canvas=this.canvasRef.current
    //     console.log(canvas)

    //     return <Bubble 
    //         canvas={this.canvasRef.current}
    //     />;
    // }

    render(){
        //createCanvas();
        return(
            <div className = "space">                
                <div className = "canvas">
                    <canvas ref={this.canvasRef} width={0} height={0} id="space_canvas">Please update your browser to use this app</canvas>
                </div>
                <Bubble
                    id= {0}
                    name= {'Costume'}
                    type= {'subject'}
                />
                <Bubble
                    id= {1}
                    name= {'On the Lot'}
                    type= {'condition'}
                />
            </div>
        );
    }    
}

// function createCanvas() {
//     var canvas = document.getElementById('canvas_picker')
//     var ctx = canvas.getContext('2d');
//     var SizeX = 0;
//     var SizeY = 0;
//     resizeCanvas();
//     window.addEventListener('resize', resizeCanvas, false);
// }

// function resizeCanvas() { //this resizes the canvas and is called when the window size changes
//     //console.log('resized')
//     SizeX = window.innerWidth*.95;
//     SizeY = window.innerHeight*.85;
//     canvas.width = SizeX;
//     canvas.height = SizeY;
//     reDraw();
// }

ReactDOM.render(<Space />, document.getElementById('root'));
