from flask import Flask
from flask import request
from flask import Response
from flask import make_response
from flask import send_file
from flask import *
from pathlib import Path
from zipfile import *
from flask_cors import CORS
import requests
import json

DEBUG=1	

app = Flask(__name__)


#
# All These Parameteres need to be included in a config file which is root read only and accessed on runtime
#

#baseURL of labFolder
labFolderBaseURL = 'https://eln.labfolder.com/api/v2'
#Testheader - required for access on labfolder, needs to be project name and a contant e-mail to be contacted when problems occur
labFolderDefaultUserAgentHeader = 'TestprojektFDM; robert.guenther@uni-bayreuth.de'
#storage base url - here the downlaoded data is stored, should terminate with a '/'
storageBaseURL = './LabFolderData/'
storageFileName = 'storage.json'
tempFolder = "./tmp/"

#couchDBConfiguration Parameters
couchDBURL = "https://127.0.0.1:5984"
couchDBAdmin = "admin"
couchDBPassword = "aodqfyUQqA"
couchDBToken = ""
couchDBStorageDatabaseName = "storage"
couchDBDocumentDatabaseName = "documents"
couchDBStaticDatabaseName = "static"


#DELETE AFTER DEV
devUserID = "bt303343"

CORS(app)

#----------------------Page Navigation-----------------------------------------
@app.route('/')
def navhome():
	return render_template("index.html")

@app.route('/impressum')
def navimpressum():
	return render_template("impressum.html")

@app.route('/history')
def navhistory():
	return render_template("history.html")

@app.route('/labfolder')
def navlabfolder():
	return render_template("labfolder.html")

@app.route('/easydb')
def naveasydb():
	return render_template("easydb.html")

#----------------------Authentification LabFolder------------------------------
@app.route('/auth/login',methods=['POST'])
def authenticateLabFolder():
    url = labFolderBaseURL + '/auth/login'
    data = request.get_data()
    headers={"Content-Type": "application/json"}            
    response = requests.post(url,data=data,headers=headers)
    return response.text

@app.route('/auth/logout', methods=['POST'])
def logoutLabFolder():
	url = labFolderBaseURL + '/auth/logout'
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }

	response = requests.post(url, headers=headers)
	return response.text             

def authenticateCouchDB():
	url = couchDBURL + '/_session'
	data =	{"name":  couchDBAdmin,	"password": couchDBPassword	}
	headers = {"Content-Type": "application/json"}            
	response = requests.post(url,data=data,headers=headers)
	if response.status_code == 200:
		cookie = response.headers["Set-Cookie"]
		couchDBToken = coookie[:cookie.find(";")]
		return True
	else:
		print("Error logging into couchDB. Wrong Username or Password!")
		return False

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

@app.route('/download', methods=['GET'])
def downloadFileToClient():
	userID = devUserID
	projectID = request.args.get('project_id', default = '', type = str)
	entryID = request.args.get('entry_id', default = '', type = str)
	entryVersionID = request.args.get('entry_version_id', default = '', type = str)
	# elementID = request.args.get('element_id', default = '', type = str)
	# versionID = request.args.get('version_id', default = '', type = str)
	path = ''
	filename = "test.zip"
	if userID != '' and projectID != '' and entryID != '' and entryVersionID != '':
		path = storageBaseURL + userID + "/" + projectID + "/" + entryID + "/" + entryVersionID
		zipfile = createZipFileFromTree(path,tempFolder + filename) # Todo name for zip file
	else:
		return app.response_class(json.dumps({'Error' : 'Missing Parameter id'}),status=200, mimetype='application/json') 
	try:
		return send_from_directory(tempFolder,filename,as_attachment=True)
	except Exception as e:
		print(e)
		return app.response_class(json.dumps({'Error' : 'Internal Error'}),status=400, mimetype='application/json') 

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
	downloadFileFromLabFolder(userID, jsonData)
	if len(jsonData) > 0:
		updateStorageFile(userID,jsonData)
	return app.response_class(status=200, mimetype='application/json') 		
    

#TODO adapt to couchdb
#@app.route('/elements/file' , methods=['GET'])
def downloadFileFromLabFolder(userID, dataArray):
	if DEBUG:
		print("-----in downloadFileFromLabFolder-----")
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
		storageURL = storageBaseURL + userID + "/" + element["projectID"] + "/" + element["entryID"] + "/" + element["entryVersionID"] + "/" + element["elementID"] + "/" + element["versionID"] + "/"
		folderPath = Path(storageURL)
		folderPath.mkdir(mode=0o777, parents=True, exist_ok=True)
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

# @app.route('/mdb/databases', methods=['GET'])
# def getMDBDatabases():
# 	url = labFolderBaseURL + '/mdb/databases'
	
# 	#prepare header		
# 	headers = {"Content-Type": "application/json",
# 				"Authorization" :  "Token " + request.headers['Authorization'],
# 				"User-Agent": labFolderDefaultUserAgentHeader
# 			  }
# 	response = requests.get(url, headers=headers)
# 	print(url)
# 	print(response.text)
# 	return response.text

@app.route('/mdb/categories', methods=['GET'])
def getMDBCategories():
	url = labFolderBaseURL + '/mdb/categories'
	#prepare header		
	headers = {"Content-Type": "application/json",
				"Authorization" :  "Token " + request.headers['Authorization'],
				"User-Agent": labFolderDefaultUserAgentHeader
			  }
	if DEBUG:			  
		print(url)
	response = requests.get(url, headers=headers)
	return response.text

#TODO adapt to couchdb
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

@app.route('/storage', methods=['GET'])
def getStorageFile():
	userID = devUserID
	return getDatastructure(userID,return_as_string=True)


def getDatastructure(userID,return_as_string=False):
	couchDBPath = couchDBURL + "/" + couchDBStorageDatabaseName + "/" + userID
	headers = {"Accept": "application/json",
				"Content-Type" : "application/json",
				"Cookie" :  couchDBToken
				} 
	response = request.get(url,headers=headers)
	if response:
		if return_as_string:
			return response.text
		else:
			return json.loads(reponse.text)
	elif response.status_code == 404:
		initialData = {"user" : userID, "projects": []}
		try:
			new_response = request.put(url,headers=headers,data=initialData)
			new_response.raise_for_status()
		except requests.exceptions.HTTPError as e:
			print("HTTP Error:",e)

# def getDatastructure(userID,return_as_string=False):
# 	folderPath = storageBaseURL + userID
# 	userDirectory = Path(folderPath)
# 	if not userDirectory.is_dir(): #check if folder already exists
# 		createUserFolder(userID)	
# 	storageFile = Path(folderPath + '/' + storageFileName)
# 	if storageFile.is_file(): #structure object already exists
# 		data = storageFile.read_text()
# 		if return_as_string:
# 			return data
# 		else:
# 			dataJSON = json.loads(data)
# 			return dataJSON
# 	else: # storage oject does not exist yet, this should never happen since creation of the folder always creates an initial storage file
# 		if return_as_string:
# 			return "{}"
# 		else:
# 			return {} #return empty object


# #creates the folder for the user if it does not exist yet. also creates an empty structure.json object
# def createUserFolder(userID):
# 	folderPath = storageBaseURL + userID
# 	if DEBUG:
# 		print("folderPath: " + folderPath)
# 	userDirectory = Path(folderPath)		
# 	try:
# 		if DEBUG:
# 			print("trying to create user folder for " + userID)
# 		userDirectory.mkdir(mode=0o700,parents=True, exist_ok=False) #create a file, and catch exception if already exists, return if so, structure file also is there
# 		storageFile = Path(folderPath + '/' + storageFileName)
# 		storageFile.touch(mode=0o700, exist_ok = True) #touch the file, catch exception (should never happen since it should never already exist)
# 		initialData = {"user" : userID, "projects": []}
# 		storageFile.write_text(json.dumps(initialData)) #initialize the file with empty array for projects and userID for further usage
# 		if DEBUG:
# 			print("finsihed creating user folder for " + userID)
# 	except FileNotFoundError:
# 		if DEBUG:
# 			print("EXCEPT in 'createUserFolder': Can't find parent folder.")
# 		return
# 	except FileExistsError:
# 		if DEBUG:
# 			print("EXCEPT in 'createUserFolder': Directory already exists.")
# 		return
# 	except: 
# 		return

#updates the storage File with the added files
def updateStorageFile(userID, addElements):
	# if DEBUG:
	# 	print("---in updateStorageFile---")
	# 	print("writing " + str(len(addElements)) + " items in file")
	storageFile = getDatastructure(userID)
	# if DEBUG:
	# 	print("storage file before process")
	# 	print(json.dumps(storageFile))
	for item in addElements:
		if len([x for x in storageFile["projects"] if x["projectID"] == item["projectID"]]) == 0: #if project does not exist yet, we need to create everything to the bottom
			storageFile["projects"].append({"projectID" : item["projectID"],
											"projectTitle" : item["projectTitle"],
											"entries" : [{
												"entryID" : item["entryID"],
												"entryTitle" : item["entryTitle"],
												"versions" : [{
													"versionID" : item["entryVersionID"],
													"versionDate" : item["versionDate"],													
													"elements" : [{
														"elementID" : item["elementID"],
														"elementType" : item["elementType"],
														"versions" : [{
															"versionID" : item["versionID"]
														}]
													}]
												}]
											}]})
		else:
			for proj in storageFile["projects"]:
				if proj["projectID"] == item["projectID"]:
					if len([x for x in proj["entries"] if x["entryID"] == item["entryID"]]) == 0:
						proj["entries"].append({"entryID" : item["entryID"],
												"entryTitle" : item["entryTitle"],
												"versions" : [{
													"versionID" : item["entryVersionID"],
													"versionDate" : item["versionDate"],													
													"elements" : [{
														"elementID" : item["elementID"],
														"elementType" : item["elementType"],
														"versions" : [{
															"versionID" : item["versionID"]
														}]
													}]
												}]
												})
						break
					else:
						for entry in proj["entries"]:
							if entry["entryID"] == item["entryID"]:
								if len([x for x in entry["versions"] if x["versionID"] == item["entryVersionID"]]) == 0:
									entry["versions"].append({	"versionID" : item["entryVersionID"],
																"versionDate" : item["versionDate"],									
																"elements" : [{
																	"elementID" : item["elementID"],
																	"elementType" : item["elementType"],
																	"versions" : [{
																		"versionID" : item["versionID"]
																	}]
																}]
															})
									break
								else:
									for version in entry["versions"]:
										if version["versionID"] == item["entryVersionID"]:
											if len([x for x in version["elements"] if x["elementID"] == item["elementID"]]) == 0:
												version["elements"].append({	"elementID" : item["elementID"],
																		  	"elementType" : item["elementType"],
																		  	"versions" : [{
																				"versionID" : item["versionID"]
																			}]
																		})
												break
											else:
												for element in entry["elements"]:
													if element["elementID"] == item["elementID"]: # on last level (=version) we dont need to check again if a version already exists. this case would have been found earlier and not come to here.
														element["versions"].append({"versionID" : item["versionID"]})
														break;										
	# if DEBUG:
		# print(json.dumps(storageFile))
		# print("storage file after process")
	folderPath = storageBaseURL + userID
	file = Path(folderPath + '/' + storageFileName)
	file.unlink()
	file.write_text(json.dumps(storageFile))

#checks if elements to download already exist in storage file. pops elements which are already existing of the checkArray 
#checkElements is a list of dicts: (projectID: str, entryID: str, elementID: str, versionID: str)
def removeAlreadyExistingTupel(userID,checkElements):
	storageFile = getDatastructure(userID)
	print(json.dumps(storageFile))
	output = []
	print("input length: " + str(len(checkElements)))
	for item in checkElements:
		newItem = True
		projectID 	   = item["projectID"]
		entryID        = item["entryID"]
		entryVersionID = item["entryVersionID"]
		elementID      = item["elementID"]
		versionID      = item["versionID"]
		if storageFile["projects"] == None:
			return checkElements
		if len(storageFile["projects"]) == 0:
			return checkElements
		for projVal in storageFile["projects"]:
			if projVal["projectID"] == projectID:
				for entryVal in projVal["entries"]:
					if entryVal["entryID"] == entryID:
						for entryVersionVal in entryVal["versions"]:
							if entryVersionVal["versionID"] == entryVersionID:
								for elementVal in entryVersionVal["elements"]:
									if elementVal["elementID"] == elementID:
										for versionVal in elementVal["versions"]:
											if versionVal["versionID"] == versionID:
												newItem = False
												break
										break
								break
						break
				break
		if newItem:
			output.append(item)
	print("output length: " + str(len(output)))
	return output

#TODO adapt to couchdb
def createZipFileFromTree(rootDir,filename):
	zf = ZipFile(filename,'w')
	rootPath = Path (rootDir)
	files = [f for f in rootPath.rglob("*") if f.is_file()]
	for file in files:
		print(file)
		absname = str(file.resolve())
		print("file absname:" + absname)
		print("file arcname:" + absname[absname.rfind("/") + 1:])
		zf.write(absname,absname[absname.rfind("/") + 1:])
	zf.close()



if __name__ == '__main__':
	authenticateCouchDB()
	# app.run(debug=True)
