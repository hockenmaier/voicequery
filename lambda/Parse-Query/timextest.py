import timex
import datetime

def test(query):
    tagText = timex.tag(query)
    print tagText
    timeExpressionString = timex.ground(tagText,datetime.datetime.today())
    print "Calling Timex with tagtext " + tagText + " and ground time: " + str(datetime.datetime.today()) 
    print timeExpressionString 
    
test("how many managers were hired last saturday?")
