export class layout{
    //properties are created in the initializeLayout() function below
}

export function initializeLayout(){
    layout.topbarX = 0;
    layout.topbarY = 0;
    layout.topbarHeight = 50;
    layout.queryTop = 15;
    layout.queryLeft = 30;
    layout.queryWidth = 700;
    
    layout.queryParsedTop = layout.topbarHeight - 10;
    layout.queryParsedWidth = 1000;
    layout.leftMargin = 30;
    layout.topMargin = layout.topbarHeight + 45;
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

    layout.conceptWidth = 235;
    layout.conceptHeight = 235;
}

export let bubblesInitialized = false;

//var lastDragStartId = '';
export class lastDragStart{
    id = '';
    type = '';
    shiftX = 0;
    shifty = 0;
}

export class BubbleDeets{
    constructor(internalId,text,typetext,bubbles,parentBubbleId, xLocation, yLocation,bubsInConcept){
        this.internalID = internalId;
        this.id = getNextBubbleID();
        this.text = text;
        this.type = typetext;        
        this.bubbles = bubbles;
        this.parentBubbleId = parentBubbleId;
        this.atHome = true;
        if (bubsInConcept){
            this.bubsInConcept = bubsInConcept;
        }else{
            this.bubsInConcept = [];
        }
        if(xLocation){
            this.xLocation = xLocation;
        }else{
            this.xLocation = nextXLocation(this.type,this.id,this.parentBubbleId);
        }
        if(xLocation){
            this.yLocation = yLocation;
        }else{
            this.yLocation = nextYLocation(this.type,this.id,this.parentBubbleId);
        }
        
    }
}

export let nextBubbleID = 0;
function getNextBubbleID(){
    const next = nextBubbleID;
    nextBubbleID++;
    return next.toString();
}

export let mockBubbleUpdates = 0;

export function randomSampleQuery(){
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
const infoValueRows = 3;

function nextXLocation(type,id,parentId){
    if (type === 'subject' | type === 'condition'){
        return layout.BubbleLeftMargin;
    }else if (type === 'info-field'){
        return layout.InfoBubbleLeft;
    }else if (type === 'info-value'){
        //console.log(((parseInt(id)-parseInt(parentId))%infoValueRows + 1)*105);
        return layout.InfoBubbleLeft + 55 + (((parseInt(id)-parseInt(parentId)-1)%infoValueRows + 1)*105);
    }else{
    return 300;
    }
}

function nextYLocation(type,id,parentId){
    //console.log(type);
    if (type === 'subject'){
        const nextY =  layout.BubbleTopMargin + subjectCount*60;
        subjectCount++;
        return nextY;
    }
    else if (type === 'condition'){
        const nextY = layout.conditionBubbleTopMargin + conditionCount*60;
        conditionCount++;
        return nextY;
    }
    else if (type === 'info-field'){
        const nextY = layout.BubbleTopMargin + infoFieldCount*55;
        infoFieldCount++;
        return nextY;
    }
    else if (type === 'info-value'){
        const nextY = layout.BubbleTopMargin + (infoFieldCount-1)*55 + 5;
        if((parseInt(id)-parseInt(parentId)-1)%infoValueRows === 2){
            infoFieldCount++;
        }
        return nextY;
    }
    else{
        return 300;
    }    
}