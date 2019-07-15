import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

class Bubble extends React.Component{
    render(){        
        const context = this.props.ctx
        return(
            <div>
                {context.beginPath()}
                {context.arc(50, 100, 100, 0, 2 * Math.PI, false)};
                {context.fillStyle = 'green'};
                {context.fill()};
                {context.lineWidth = 5};
                {context.strokeStyle = '#003300'};
                {context.stroke()};
            </div>
        );
    }
}

class Space extends React.Component{
    constructor(props){
        super(props);
        this.state = {          
          canvas: document.getElementById('space_canvas'),
          ctx: null,
        };
        // console.log(ctx)
      }

    componentDidMount(){
        //creating the canvas here
        const canvas = this.refs.canvas
        const mycanvas = React.createContext(canvas)
        const ctx = canvas.getContext('2d');
        this.setState({
            canvas: canvas,
            ctx: ctx
        })
        
        console.log(canvas);
        console.log(this.state.canvas);
        console.log(this.context.mycanvas)
        console.log(ctx);
        console.log(this.state.ctx);
        // console.log(ctx)
        this.resizeCanvas();
        //window.addEventListener('resize', this.resizeCanvas, false);
    }
    
    resizeCanvas() { //this resizes the canvas and is called when the window size changes
        //console.log('resized')
        const canvas = this.refs.canvas
        //const canvas = this.state.canvas;
        const SizeX = window.innerWidth*.9;
        const SizeY = window.innerHeight*.6;
        canvas.width = SizeX;
        canvas.height = SizeY;
    }

    renderBubble(){
        //const canvas = this.refs.canvas
        //const ctx = canvas.getContext('2d');
        return <Bubble 
            ctx={this.state.ctx}
        />;
    }

    render(){
        //createCanvas();
        return(
            <div className = "space">                
                <div className = "canvas">
                    <canvas ref="canvas" width={0} height={0} id="space_canvas">Please update your browser to use this app</canvas>
                </div>
                {/* {this.renderBubble()} */}
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
