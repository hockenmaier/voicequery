import axios from 'axios';

//var lastDragStartId = '';
export class lastDragStart{
    id = '';
    type = '';
    shiftX = 0;
    shifty = 0;
}

//let mockBubbleUpdates = 0;

export class layout{
    //properties are created in the initializeLayout() function below
}

export function initializeLayout(){
    layout.topbarX = 0;
    layout.topbarY = 0;
    layout.topbarHeight = 50;
    layout.queryTop = 15;
    layout.queryWidth = 700;
    
    layout.leftMargin = 15;
    layout.topMargin = layout.topbarHeight + 15;
    layout.rightMargin = 15;
    layout.bottomMargin = 20;
    layout.roomBuffer = 20;
    
    //Information Panel
    layout.infoHeight = (window.innerHeight - layout.topbarHeight) * .382;
    layout.infoSpacing = 3;
    
    //Subject and Condition Panel
    layout.lexTop = layout.topMargin + layout.infoHeight + layout.roomBuffer
    layout.subjectBottom = window.innerHeight/2 + (layout.roomBuffer/2);
    layout.lexWidth = 155;
    layout.queryLeft = layout.lexWidth + layout.leftMargin;
    layout.homeWidth = 70;
    layout.homeLeft = layout.leftMargin + 5;
    
    layout.conditionBottom = layout.roomBuffer;
    layout.conditionTop = window.innerHeight/2 + (layout.roomBuffer/2);
    layout.conditionLeft = layout.leftMargin + layout.lexWidth + layout.roomBuffer
    
    layout.BubbleRoomLeftMargin = 20;
    layout.BubbleRoomTopMargin = -30;
    layout.BubbleLeftMargin = layout.leftMargin + layout.BubbleRoomLeftMargin;
    layout.BubbleTopMargin = layout.topMargin + layout.BubbleRoomTopMargin;
    layout.conditionBubbleTopMargin = layout.conditionTop + layout.BubbleRoomTopMargin;
    
    //Concept Panel
    layout.conceptWidth = 155;
    
    // Answer Area
    layout.queryResponseLeft = layout.leftMargin + layout.lexWidth*2 + layout.roomBuffer*2;
    layout.queryResponseTop = layout.topMargin + layout.infoHeight + layout.roomBuffer;
    
    layout.bubbleHeight = {
      'subject': 50,
      'condition': 50,
      'info-field': 40,
      'info-value': 36,
      'concept': 160,
    };
    
    layout.bubbleWidth = {
      'subject': 120,
      'condition': 120,
      'info-field': 150,
      'info-value': 150,
      'concept': 160,
    };
}

export function randomSampleQuery(){
    let queries = [];
    queries.push("How many female employees are in Engineering?");
    queries.push("What is the average salary of employees with doctorate's degrees?");
    queries.push("What is the median tenure of manager level employees in the US?");
    queries.push("How many entry-level employees were hired last April?");
    queries.push("How many leads did Anne Smith generate in 2015?");
    queries.push("Sum our spend on data storage services in Azure this year to date.");
    queries.push("What was the total forecasted revenue for deals won in Europe in 2014?");
    queries.push("What was the median revenue goal for startups in 2013?");
    queries.push("How many enterprises are we working with in Asia?");
    const randomInt = Math.floor(Math.random()*queries.length);
    //console.log(queries[randomInt]);
    return queries[randomInt];
}

export function sendParseLambdaBootMessage(workspace){
        console.log('Sending lambda boot parse http call')
        // var self = this;
        axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/parse', {
            query: '.',
            workspace: workspace
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
    
export function sendSaveConceptLambdaBootMessage(workspace){
    console.log('Sending lambda boot save-concept http call')
    // var self = this;
    axios.post('https://j43d6iu0j3.execute-api.us-west-2.amazonaws.com/Dev/vq/save-concept', {
        internal_ID: '.',
        workspace: workspace,
        text: '',
        concept_item_detail: '',
        concept_items: '',
        useHyponymNames: true
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