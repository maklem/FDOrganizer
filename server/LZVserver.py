from flask import Flask
from flask import request
from flask import Response
from flask import make_response
from flask import send_file
from pathlib import Path
from flask_cors import CORS
import requests
import json

DEBUG=1	

app = Flask(__name__)
#baseURL of labFolder
labFolderBaseURL = 'https://eln.labfolder.com/api/v2'
#Testheader - required for access on labfolder, needs to be project name and a contant e-mail to be contacted when problems occur
labFolderDefaultUserAgentHeader = 'TestprojektFDM; robert.guenther@uni-bayreuth.de'
#storage base url - here the downlaoded data is stored, should terminate with a '/'
storageBaseURL = './data/'
storageFileName = 'storage.json'

#DELETE AFTER DEV
devUserID = "bt303343"

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

@app.route('/elements/download', methods=['POST'])
def download():
	#we also need to verify the loged in ldap user here
	#data should contain a json object with structure:
	#{
	#	elementType: [IMAGE,TABLE,TEXT],
	#	elementID: elementID
	#}
	userID = devUserID
	data = request.get_data()
	jsonData = json.loads(data)
	jsonData = removeAlreadyExistingTupel(userID, jsonData)            
	downloadFile(userID, jsonData)
	if len(jsonData) > 0:
		updateStorageFile(userID,jsonData)
	return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'} 		
    


#@app.route('/elements/file' , methods=['GET'])
def downloadFile(userID, dataArray):
	if DEBUG:
		print("-----in downloadFile-----")
	for element in dataArray:		
		if element["elementType"] == 'IMAGE':
			url = labFolderBaseURL + '/elements/file/'
			file_info_url = url + element["elementID"]	
			file_url = file_info_url + '/download'
		elif element["elementType"] == 'TABLE':
			url = labFolderBaseURL + '/elements/table/'
			file_url = url + element["elementID"]	
		elif element["elementType"] == 'TEXT':
			url = labFolderBaseURL + '/elements/text/'
			file_url = url + element["elementID"]								
		else:
			return

		headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }
		#element["elementID"] = request.args.get('id', default = '', type = str)
		# if element["elementID"] == '':
		# 	return json.dumps({'Error' : 'Missing Parameter id'}), 400, {'Content-Type' : 'application/json'} 

		fileResponse = requests.get(file_url, headers=headers)
		storageURL = storageBaseURL + userID + "/" + element["projectID"] + "/" + element["entryID"] + "/" + element["elementID"] + "/" + element["versionID"] + "/"
		folderPath = Path(storageURL)
		folderPath.mkdir(mode=0o700, parents=True, exist_ok=True)
		print(storageURL)
		if element["elementType"] == 'IMAGE':
			fileInfoResponse = requests.get(file_info_url, headers=headers)
			fileInfoResponseJDATA = json.loads(fileInfoResponse.text)
			filename = fileInfoResponseJDATA["file_name"]
			filedata = fileInfoResponseJDATA["version_date"]
			fileversion = fileInfoResponseJDATA["version_id"]
			fileData = fileResponse.content
			try:
				if DEBUG:
					print("---trying to write image file")
				file = open(storageURL + filename, "wb")
				file.write(fileData)
			except:
				print("Error Saving image file")	
		elif element["elementType"] == 'TABLE':
			# fileResponse = requests.get(file_url, headers=headers)
			if DEBUG:
					print("---trying to write table file")
			fileInfoResponseJDATA = json.loads(fileResponse.text)
			title = fileInfoResponseJDATA["title"]
			date = fileInfoResponseJDATA["version_date"]
			version = fileInfoResponseJDATA["version_id"]
			content = fileInfoResponseJDATA["content"]
			
			sheets = content["sheets"]

			# print(sheets)
			for sheetKey in sheets:
				try:			
					data = sheets[sheetKey]["data"]["dataTable"]
				except:
					if DEBUG:
						print("no data in sheet " + sheetKey)
					return
				sheetName = sheets[sheetKey]["name"]
				fileData = ""
				for line in data:
					for row in data[line]:
						append = data[line][row]["value"]
						if type(append) is int:
							append = str(append)
						fileData = fileData + append + ","
					fileData = fileData.rstrip(",")
					fileData = fileData + "\n"
				try:
					print("opening")
					file = Path(storageURL + title + "-" + sheetName + ".csv")
					# file = open(storageURL + title + "-" + sheetName + ".csv", "w")
					print("opened")
					file.write_text(fileData)
					print("written")
					print("closed")
				except:
					print("Error Saving table file")				
		elif element["elementType"] == 'TEXT':
			if DEBUG:
					print("---trying to write text file")
			# fileResponse = requests.get(file_url, headers=headers)
			fileInfoResponseJDATA = json.loads(fileResponse.text)
			date = fileInfoResponseJDATA["version_date"]
			version = fileInfoResponseJDATA["version_id"]
			fileData = fileInfoResponseJDATA["content"]
			try:
				file = open(storageURL + "test" + ".txt", "w")
				file.write(fileData)
			except:
				print("Error Saving text file")			

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
def downloadMDBItems():
	urlItems = labFolderBaseURL + '/mdb/items'
	urlCategories = labFolderBaseURL + '/mdb/categories'
	categoryID = request.args.get('category_id', default = '', type = str)
	if categoryID == '':
		return json.dumps({'Error' : 'Missing Parameter id'}), 400, {'Content-Type' : 'application/json'} 
	urlItems = urlItems + '?category_id=' + categoryID		
	urlCategories = urlCategories + '/' + categoryID
	#prepare header		
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }
	if DEBUG:			  
		print(urlItems)
		print(urlCategories)
	responseCategories = requests.get(urlCategories, headers=headers)
	responseItems = requests.get(urlItems, headers=headers)
	if DEBUG:
		print(responseCategories.text)
		print(responseItems.text)
	#now we preprocess the answer to a csv 
	categoryResponseJDATA = json.loads(responseCategories.text)
	itemResponseJDATA = json.loads(responseItems.text)
	
	attributes = categoryResponseJDATA["attributes"]
	attributes_sorted = sorted(attributes, key=lambda x: x["display_order"])
	title = categoryResponseJDATA["title"]

	fileData = "Name, "
	for att in attributes_sorted:
		fileData = fileData + att["title"] + ","
	fileData.rstrip(",")
	fileData = fileData + "\n"
	if DEBUG:
		print("After headline")
		print(fileData)

	for item in itemResponseJDATA:
		fileData = fileData + item["title"] + ","
		for satt in attributes_sorted:
			#write the content of the sorted attribute field. identified by the id of the attribute
			fileData = fileData + item["custom_attributes"][satt["id"]] + ","
		fileData.rstrip(",")
		fileData = fileData + "\n"
	if DEBUG:		
		print("After Content")
		print(fileData)		
	file = open(title + ".csv", "w")
	file.write(fileData)
	file.close
	return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'} 

@app.route('/history', methods=['GET'])
def getHistory():
	i=0
	#TODO NEED TO BE IMPLEMENTED WHEN AUTH WITH LDAP IS DONE SO WE CAN VERIFY THE USER
	#getDatastructure and return it as json file

def getDatastructure(userID):
	folderPath = storageBaseURL + userID
	userDirectory = Path(folderPath)
	if userDirectory.is_dir(): #check if folder already exists
		storageFile = Path(folderPath + '/' + storageFileName)
		if storageFile.is_file(): #structure object already exists
			data = storageFile.read_text()
			dataJSON = json.loads(data)
			return dataJSON
		else: # storage oject does not exist yet, this should never happen since creation of the folder always creates an initial storage file
			return {} #return empty object
	else: # directory doesnt exist yet, return empty object
		createUserFolder(userID)

#creates the folder for the user if it does not exist yet. also creates an empty structure.json object
def createUserFolder(userID):
	folderPath = storageBaseURL + userID
	if DEBUG:
		print("folderPath: " + folderPath)
	userDirectory = Path(folderPath)		
	try:
		if DEBUG:
			print("trying to create user folder for " + userID)
		userDirectory.mkdir(mode=0o700,parents=True, exist_ok=False) #create a file, and catch exception if already exists, return if so, structure file also is there
		storageFile = Path(folderPath + '/' + storageFileName)
		storageFile.touch(mode=0o700, exist_ok = True) #touch the file, catch exception (should never happen since it should never already exist)
		initialData = {"user" : userID, "projects": []}
		storageFile.write_text(json.dumps(initialData)) #initialize the file with empty array for projects and userID for further usage
		if DEBUG:
			print("finsihed creating user folder for " + userID)
	except FileNotFoundError:
		if DEBUG:
			print("EXCEPT in 'createUserFolder': Can't find parent folder.")
		return
	except FileExistsError:
		if DEBUG:
			print("EXCEPT in 'createUserFolder': Directory already exists.")
		return
	except: 
		return

#updates the storage File with the added files
def updateStorageFile(userID, addElements):
	storageFile = getDatastructure(userID)
	for item in addElements:
		if len([x for x in storageFile["projects"] if x["projectID"] == item["projectID"]]) == 0: #if project does not exist yet, we need to create everything to the bottom
			storageFile["projects"].append({"projectID" : item["projectID"],
											"projectTitle" : item["projectTitle"],
											"entries" : [{
												"entryID" : item["entryID"],
												"entryTitle" : item["entryTitle"],
												"elements" : [{
													"elementID" : item["elementID"],
													"elementType" : item["elementType"],
													"versions" : [{
														"versionID" : item["versionID"]
													}]
												}]
											}]})
		else:
			for proj in storageFile["projects"]:
				if proj["projectID"] == item["projectID"]:
					if len([x for x in proj["entries"] if x["entryID"] == item["entryID"]]) == 0:
						proj["entries"].append({"entryID" : item["entryID"],
												"entryTitle" : item["entryTitle"],
												"elements" : [{
													"elementID" : item["elementID"],
													"elementType" : item["elementType"],
													"versions" : [{
														"versionID" : item["versionID"]
													}]
												}]
												})
					else:
						for entry in proj["entries"]:
							if entry["entryID"] == item["entryID"]:
								if len([x for x in entry["elements"] if x["elementID"] == item["elementID"]]) == 0:
									entry["elements"].append({
													"elementID" : item["elementID"],
													"elementType" : item["elementType"],
													"versions" : [{
														"versionID" : item["versionID"]
													}]
												})
								else:
									for element in entry["elements"]:
										if element["elementID"] == item["elementID"]: # on last level (=version) we dont need to check again if a version already exists. this case would have been found earlier and not come to here.
											element["versions"].append({"versionID" : item["versionID"]}) #TODO: Add title of file in the document										

#checks if elements to download already exist in storage file. pops elements which are already existing of the checkArray 
#checkElements is a list of dicts: (projectID: str, entryID: str, elementID: str, versionID: str)
def removeAlreadyExistingTupel(userID,checkElements):
	storageFile = getDatastructure(userID)
	print(json.dumps(storageFile))
	output = []
	for item in checkElements:
		projectID = item["projectID"]
		entryID   = item["entryID"]
		elementID = item["elementID"]
		versionID = item["versionID"]
		if len(storageFile["projects"]) == 0:
			return checkElements
		for projKey,projVal in storageFile["projects"].items():
			if projVal["projectID"] == projectID:
				for entryKey, entryVal in projVal["entries"]:
					if entryVal["entryID"] == entryID:
						for elementKey, elementVal in entryVal["elements"]:
							if elementVal["elementID"] == elementID:
								for versionKey, versionVal in elementVal["versions"]:
									if versionVal["versionID"] == versionID:
										continue
		output.append(item)
	return output



if __name__ == '__main__':
	app.run(debug=True)