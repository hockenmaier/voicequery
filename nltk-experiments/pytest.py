import json

data = {}
data['key'] = 'value'
json_data = json.dumps(data)

print('JSON: ', json_data)


test = "this is a test"
print(test)

replace = test.replace('test','replace')
print(replace)