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
    layout.queryLeft = 30;    
    layout.queryWidth = 700;
    
    layout.queryResponseTop = layout.topbarHeight - 1;
    layout.queryResponseWidth = 1000;
    layout.leftMargin = 30;
    layout.topMargin = layout.topbarHeight + 15;
    layout.rightMargin = 30;

    layout.subjectHeight = 380;
    layout.subjectWidth = 165;

    layout.queryResponseLeft = layout.leftMargin + layout.subjectWidth + 15;

    layout.roomBuffer = 20;
    layout.conditionTop = layout.topMargin + layout.subjectHeight + layout.roomBuffer;
    layout.conditionHeight = 380;
    layout.conditionWidth = 165;

    layout.infoHeight = layout.conditionHeight + layout.subjectHeight + layout.roomBuffer;
    layout.infoWidth = 500;

    layout.BubbleRoomLeftMargin = 20;
    layout.BubbleRoomTopMargin = 30;
    layout.BubbleLeftMargin = layout.leftMargin + layout.BubbleRoomLeftMargin;
    layout.BubbleTopMargin = layout.topMargin + layout.BubbleRoomTopMargin;
    layout.conditionBubbleTopMargin = layout.conditionTop + layout.BubbleRoomTopMargin;

    layout.InfoBubbleLeft = window.innerWidth - (layout.infoWidth + layout.rightMargin - layout.BubbleRoomLeftMargin);

    layout.conceptWidth = 180;
    layout.conceptHeight = 160;
}