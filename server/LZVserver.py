from flask import Flask
from flask import request
from flask import Response
from flask import make_response
from flask import send_file
from flask_cors import CORS
import requests
import json

DEBUG=1

app = Flask(__name__)
labFolderBaseURL = 'https://eln.labfolder.com/api/v2'
labFolderDefaultUserAgentHeader = 'TestprojektFDM; robert.guenther@uni-bayreuth.de'
CORS(app)

#----------------------Authentification----------------------------------------
@app.route('/auth/login',methods=['POST'])
def authenticate():
    url = labFolderBaseURL + '/auth/login'
    data = request.get_data()
    headers={"Content-Type": "application/json"}            
    response = requests.post(url,data=data,headers=headers)
    return response.text

@app.route('/auth/logout', methods=['POST'])
def logout():
	url = labFolderBaseURL + '/auth/logout'
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }

	response = requests.post(url, headers=headers)
	return response.text             

#----------------------Projects------------------------------------------------

@app.route('/projects', methods=['GET'])
def getProjects():
	url = labFolderBaseURL + '/projects?'
	mod = 0
	#process optional parameters and add them to url if required
	group_id = request.args.get('group_id', default = '', type = str)
	if group_id != '' :
		mod = 1
		url = url + 'group_id=' + group_id + '&'	
	owner_id = request.args.get('owner_id', default = '', type = str) 
	if owner_id != '' :
		mod = 1
		url = url + 'owner_id=' + owner_id + '&'
	only_root_level = request.args.get('only_root_level', default = 0, type = int) 
	if only_root_level:
		mod = 1
		url = url + 'only_root_level=true&'
	folder_id = request.args.get('folder_id', default = '', type = str) 
	if folder_id != '' :
		mod = 1
		url = url + 'folder_id=' + folder_id + '&'
	projects_ids = request.args.get('projects_ids', default = '', type = str) 
	if projects_ids != '' :
		mod = 1
		url = url + 'projects_ids=' + projects_ids + '&'
	limit = request.args.get('limit', default = 20, type = int) 
	if limit != 20 :
		mod = 1
		url = url + 'limit=' + str(limit) + '&'
	offset = request.args.get('offset', default = 0, type = int)  
	if offset != 0 :
		mod = 1
		url = url + 'offset=' + str(offset) + '&'
	#remove '?' from url when no parameter has been added - basically just reset it to default
	if mod == 0:
		url = url.rstrip('?')
	else: 
		url = url.rstrip('&')
	#prepare header		
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }
	response = requests.get(url, headers=headers)
	return response.text

#-------------------Notebook---------------------------------------------------

@app.route('/entries', methods=['GET'])
def getNotebookEntries():
	url = labFolderBaseURL + '/entries?'
	mod = 0
	#process optional parameters and add them to url if required <- !!!currently not yet tested!!!
	sort = request.args.get('sort', default = '', type = str)
	if sort != '' :
		mod = 1
		url = url + 'sort=' + sort + '&'	
	omni_empty_title = request.args.get('omni_empty_title', default = 0, type = int) 
	if omni_empty_title:
		mod = 1
		url = url + 'omni_empty_title=true&'
	title = request.args.get('title', default = '', type = str) 
	if title != '':
		mod = 1
		url = url + 'title=' + title + '&'
	limit = request.args.get('limit', default = 20, type = int) 
	if limit != 20 :
		mod = 1
		url = url + 'limit=' + str(limit) + '&'
	offset = request.args.get('offset', default = 0, type = int)  
	if offset != 0 :
		mod = 1
		url = url + 'offset=' + str(offset) + '&'
	expand = request.args.get('expand', default = '', type = str) 
	if expand != '':
		mod = 1
		url = url + 'expand=' + expand + '&'		
	#remove '?' from url when no parameter has been added - basically just reset it to default
	if mod == 0:
		url = url.rstrip('?')
	else:
		url = url.rstrip('&')
	#prepare header		
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }
	response = requests.get(url, headers=headers)
	return response.text

@app.route('/elements/file' , methods=['GET'])
def getFile():
	if DEBUG:
		print("-----in getFile-----")
	url = labFolderBaseURL + '/elements/file/'
	elementID = request.args.get('id', default = '', type = str)
	if elementID == '':
		return json.dumps({'Error' : 'Missing Parameter id'}), 400, {'Content-Type' : 'application/json'} 
	file_info_url = url + elementID	
	file_url = file_info_url + '/download'
	headers = {"Content-Type": "application/json",
			"Authorization" :  "Token " + request.headers['Authorization'],
			"User-Agent": labFolderDefaultUserAgentHeader
		  }
	fileInfoResponse = requests.get(file_info_url, headers=headers)
	fileResponse = requests.get(file_url, headers=headers)
	fileInfoResponseJDATA = json.loads(fileInfoResponse.text)
	
	filename = fileInfoResponseJDATA["file_name"]
	filedate = fileInfoResponseJDATA["version_date"]
	fileversion = fileInfoResponseJDATA["version_id"]
	filetype = fileInfoResponseJDATA["content_type"]
	if DEBUG:
		print('filetype: ' + filetype)
		print('filename: ' + filename)
		print('filedata: ' + filedate)
	
	file = open(filename, "wb")
	fileData = fileResponse.content
	file.write(fileData)
	file.close
	
	return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'} 

@app.route('/elements/table', methods=['GET'])
def getTable():
	if DEBUG:
		print("-----in getTable-----")
	url = labFolderBaseURL + '/elements/table/'
	elementID = request.args.get('id', default = '', type = str)
	if elementID == '':
		return json.dumps({'Error' : 'Missing Parameter id'}), 400, {'Content-Type' : 'application/json'} 
	file_url = url + elementID	
	headers = {"Content-Type": "application/json",
			"Authorization" :  "Token " + request.headers['Authorization'],
			"User-Agent": labFolderDefaultUserAgentHeader
		  }
	fileResponse = requests.get(file_url, headers=headers)
	fileInfoResponseJDATA = json.loads(fileResponse.text)
	
	title = fileInfoResponseJDATA["title"]
	date = fileInfoResponseJDATA["version_date"]
	version = fileInfoResponseJDATA["version_id"]
	content = fileInfoResponseJDATA["content"]

	#process the table data and write it to a file as csv, save this file on storage
	sheets = content["sheets"]
	for sheet_key in sheets:
		if DEBUG:
			print("key: " + sheet_key)
		file = open(title + ".csv", "w")
		data = sheets[sheet_key]["data"]["dataTable"]
		if DEBUG:
			print("data: " + str(data))
		fileData = ""
		for line in data:
			for row in data[line]:
				append = data[line][row]["value"]
				if type(append) is int:
					append = str(append)
				fileData = fileData + append + ","
			fileData = fileData.rstrip(",")
			fileData = fileData + "\n"
		if DEBUG:
			print("fileData: " + fileData)
		file.write(fileData)
		file.close
	return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'} 

@app.route('/elements/text', methods=['GET'])
def getText():
	if DEBUG:
		print("-----in getText-----")
	url = labFolderBaseURL + '/elements/text/'
	elementID = request.args.get('id', default = '', type = str)
	if elementID == '':
		return json.dumps({'Error' : 'Missing Parameter id'}), 400, {'Content-Type' : 'application/json'} 
	file_url = url + elementID	
	headers = {"Content-Type": "application/json",
			"Authorization" :  "Token " + request.headers['Authorization'],
			"User-Agent": labFolderDefaultUserAgentHeader
		  }
	fileResponse = requests.get(file_url, headers=headers)
	fileInfoResponseJDATA = json.loads(fileResponse.text)
	
	date = fileInfoResponseJDATA["version_date"]
	version = fileInfoResponseJDATA["version_id"]
	content = fileInfoResponseJDATA["content"]
	print(content)
	#process the table data and write it to a file as csv, save this file on storage
	file = open("test" + ".txt", "w")
	file.write(content)
	file.close()
	return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'} 

#------------Material Database-------------

@app.route('/mdb/databases', methods=['GET'])
def getMDBDatabases():
	url = labFolderBaseURL + '/mdb/databases'
	
	#prepare header		
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }
	response = requests.get(url, headers=headers)
	return response.text

@app.route('/mdb/categories', methods=['GET'])
def getMDBCategories():
	url = labFolderBaseURL + '/mdb/categories'
	elementID = request.args.get('mdb_id', default = '', type = str)
	if elementID == '':
		return json.dumps({'Error' : 'Missing Parameter id'}), 400, {'Content-Type' : 'application/json'} 
	url = url + '?mdb_id=' + elementID
	#prepare header		
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }
	if DEBUG:			  
		print(url)
	response = requests.get(url, headers=headers)
	return response.text

#----does only support filtering by categoryID----
@app.route('/mdb/items', methods=['GET'])
def getMDBItems():
	url = labFolderBaseURL + '/mdb/items'
	categoryID = request.args.get('category_id', default = '', type = str)
	if categoryID != '':
		url = url + '?category_id=' + categoryID		
	#prepare header		
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }
	print(url)			  
	response = requests.get(url, headers=headers)
	print(response.text)
	return response.text

if __name__ == '__main__':
	app.run(debug=True)