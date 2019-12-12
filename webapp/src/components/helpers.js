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
    layout.leftMargin = 20;
    layout.topMargin = layout.topbarHeight + 15;
    layout.rightMargin = 20;
    layout.bottomMargin = 20;
    layout.roomBuffer = 20;
    
    layout.subjectBottom = window.innerHeight/2 + (layout.roomBuffer/2);
    layout.lexWidth = 155;
    
    layout.queryResponseLeft = layout.leftMargin + layout.subjectWidth + 150;
    
    layout.conditionBottom = layout.roomBuffer;
    layout.conditionTop = window.innerHeight/2 + (layout.roomBuffer/2);
    
    layout.infoWidth = 500;
    
    layout.BubbleRoomLeftMargin = 20;
    // layout.BubbleRoomTopMargin = 30;
    layout.BubbleRoomTopMargin = -30;
    layout.BubbleLeftMargin = layout.leftMargin + layout.BubbleRoomLeftMargin;
    layout.BubbleTopMargin = layout.topMargin + layout.BubbleRoomTopMargin;
    layout.conditionBubbleTopMargin = layout.conditionTop + layout.BubbleRoomTopMargin;
    
    layout.InfoBubbleLeft = window.innerWidth - (layout.infoWidth + layout.rightMargin - layout.BubbleRoomLeftMargin);
    
    // layout.conceptWidth = 180;
    // layout.conceptHeight = 160;
    
    layout.conceptRoomHeight = 150;
    layout.conceptRoomBottomMargin = layout.roomBuffer;
    layout.conceptRoomRight = layout.infoWidth + layout.leftMargin + layout.roomBuffer;
    layout.conceptRoomLeft = layout.lexWidth + layout.leftMargin + layout.roomBuffer;
    
    layout.bubbleHeight = {
      'subject': 50,
      'condition': 50,
      'info-field': 40,
      'info-value': 30,
      'concept': 160,
    };
    
    layout.bubbleWidth = {
      'subject': 120,
      'condition': 120,
      'info-field': 150,
      'info-value': 90,
      'concept': 160,
    };
    
}