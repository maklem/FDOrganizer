"""
Module for creation of mets files.
"""
import json

allowed_metadata_identifer = ["dublin_core_1_1"]
ctr_id_map = {}


def enrich_ingest_with_package_data(ingest, storage_file):
    """
    recursivly enhances the packages data by replacing in "content.child_data_objects" the id
    with new json objects containing the actual file information. This is expected to be done
    before creating the export xml string to simplify processing. expects the ingest, returns
    json object.
    """
    new_con = []
    for item in ingest["content"]:
        recursive_enrich_package_content(item["package_data"], storage_file)
        new_con.append(item)
    ingest["content"] = new_con
    return ingest


def recursive_enrich_package_content(package, storage_file):
    """
    resursive function call to enrich the content of the package file
    """
    new_con = []
    for content in package["child_data_objects"]:
        append = [item for item in storage_file if content == item["package_id"]][0]
        if append["type"] == "PACKAGE":
            recursive_enrich_package_content(append, storage_file)
        new_con.append(append)
    package["child_data_objects"] = new_con


def get_ingest_data_files(ingest):
    """
    returns a list of all data files under a ingest file.
    """
    flat_data = []
    for item in ingest["content"]:
        flat_data.append(
            {
                "root_package": item["package_id"],
                "flat_data": get_all_data_files(item["package_data"]),
            }
        )
    return flat_data


def get_all_data_files(package):
    """
    returns a list oft all data objects in the package. recursevily travels through the hierachical
    package structures
    """
    files = []
    if package["type"] == "DATA":
        files.append(package)
    else:  # type == package
        for item in package["child_data_objects"]:
            files += get_all_data_files(item)
    return files


def generate_structmap(ingest):
    """
    based on package structure, create a mets:structmap.
    return this as xml string.
    """
    ctr = 1
    smap = '<mets:structMap TYPE="Logical" ID="rep1-2">'
    smap += '<mets:div ID="id_' + ingest["ingest_id"] + '" LABEL="' + ingest["name"] + '">'
    for con in ingest["content"]:
        smap += (
            '<mets:div ID="id_'
            + con["package_id"]
            + '" LABEL="'
            + con["package_data"]["name"]
            + '">'
        )
        for item in con["package_data"]["child_data_objects"]:
            add, ctr = rec_gen_smap(item, ctr)
            smap += add
        smap += "</mets:div>"
    smap += "</mets:div>"
    smap += "</mets:structMap>"
    return smap


def rec_gen_smap(package, ctr):
    """
    recursively generates the structmap data
    """
    smap = ""
    if package["type"] == "DATA":
        smap += '<mets:div LABEL="FILE_TUPLE">'
        smap += '<mets:div LABEL="FILE">'
        smap += '<mets:fptr FILEID="fid' + str(ctr) + '-1"/>'
        ctr_id_map[package["package_id"]] = str(ctr)
        ctr = ctr + 1
        smap += '</mets:div>'
        smap += '<mets:div LABEL="METADATA">'
        smap += '<mets:fptr FILEID="fid' + str(ctr) + '-1"/>'
        ctr_id_map[package["package_id"]+"_meta"] = str(ctr)
        ctr = ctr + 1
        smap += '</mets:div>'
        smap += '</mets:div>'
    else:
        smap += (
            '<mets:div ID="id_' + package["package_id"] + '" LABEL="' + package["name"] + '">'
        )
        for item in package["child_data_objects"]:
            add, ctr = rec_gen_smap(item, ctr)
            smap += add
        smap += "</mets:div>"
    return smap, ctr


def generate_dmd_for_meta(file_meta, identifier, create_origin_uuid_metadata=False,\
                            content_origin="", origin_uuid=""):
    """
    generate a dmd for each file. always required at least for the origin_uuid
    return this as xml string.
    """
    if not file_meta["identifier"] in allowed_metadata_identifer:
        return {"successfull": False, "content": "Invalid metadata scheme for dmd Data"}
    dmd = ""
    dmd += '<mets:dmdSec ID="' + identifier + '">'
    dmd += '<mets:mdWrap MDTYPE="DC">'
    dmd += "<mets:xmlData>"
    dmd += (
        '<dc:record xmlns:dc="http://purl.org/dc/elements/1.1/"'
        + ' xmlns:dcterms="http://purl.org/dc/terms/"'
        + ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
    )
    for item in file_meta["fields"]:
        for val in item["values"]:
            dmd += (
                "<dc:"
                + item["field_identifier"]
                + ">"
                + val
                + "</dc:"
                + item["field_identifier"]
                + ">"
            )
    if create_origin_uuid_metadata:
        dmd += "<dc:identifier>" + origin_uuid +"</dc:identifier>"
        #TODO this @UBT needs to be changed to a variable based on users institution as soon as user
        #management is implemented
        dmd += "<dc:source>" + content_origin +"@UBT</dc:source>"
    dmd += "</dc:record>"
    dmd += "</mets:xmlData>"
    dmd += "</mets:mdWrap>"
    dmd += "</mets:dmdSec>"
    return {"successfull": True, "content": dmd}


def generate_amd_for_file(amd_meta, counter, generate_checksums=True):
    """
    generate a techMD section with repository specific metadata:
    amd_meta in structure:
    {"section1" : {"metafield" : "metavalue"}, "section2":{"metafield": "value"}, ...}
    return this as xml string.
    """
    amd = ""
    amd += '<mets:amdSec ID="fid'+counter+'-1-amd">'
    amd += '<mets:techMD ID="fid'+counter+'-1-amd-tech">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx">'
    amd += '<section id="generalFileCharacteristics">'
    amd += '<record>'
    amd += '<key id="fileMIMEType">' + str(amd_meta['file_type']) + '</key>'
    amd += '<key id="fileOriginalName">' + str(amd_meta['filename']) + '</key>'
    amd += "</record>"
    amd += "</section>"
    print("amd_meta")
    print(json.dumps(amd_meta))
    if generate_checksums:
        amd += '<section id="fileFixity">'
        for fixity in amd_meta["checksums"]:
            amd += '<record>'
            amd += '<key id="fixityType">' + fixity["type"] + '</key>'
            amd += '<key id="fixityValue">' + fixity["hash"] + '</key>'
            amd += '</record>'
        amd += '</section>'
    '''
    rework with a mapping from metadata to rosetta dnx fields. this should map metadata from
    Step1: fill dnx metadata with data_object_metadata for file objects.
    Step2: Create an additional json file, containing the origin_metadata for each object. This needs to be handled in mets file too.
    '''
    # for sec_key in amd_meta:
    #     for key in amd_meta[sec_key]:
    #         amd += '<key id="' + sec_key + '_' + key + '">' + str(amd_meta[sec_key][key]) + "</key>"
    amd += "</dnx>"
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:techMD>"
    amd += '<mets:rightsMD ID="fid'+counter+'-1-amd-rights">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx"/>'
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:rightsMD>"
    amd += '<mets:sourceMD ID="fid'+counter+'-1-amd-source">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx"/>'
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:sourceMD>"
    amd += '<mets:digiprovMD ID="fid'+counter+'-1-amd-digiprov">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += "<dnx xmlns='http://www.exlibrisgroup.com/dps/dnx'/>"
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:digiprovMD>"
    amd += "</mets:amdSec>"
    return amd


def generate_amd_for_rep():
    '''
    generate the administrative metadata for a representation. in out system, rep equals the package
    level.
    '''
    amd = ""
    amd += '<mets:amdSec ID="rep1-amd">'
    amd += '<mets:techMD ID="rep1-amd-tech">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx">'
    amd += '<section id="generalRepCharacteristics">'
    amd += '<record>'
    amd += '<key id="preservationType">PRESERVATION_MASTER</key>'
    amd += '<key id="usageType">VIEW</key>'
    amd += '<key id="RevisionNumber">1</key>'
    amd += "</record>"
    amd += "</section>"
    amd += "</dnx>"
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:techMD>"
    amd += '<mets:rightsMD ID="rep1-amd-rights">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx"/>'
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:rightsMD>"
    amd += '<mets:sourceMD ID="rep1-amd-source">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx"/>'
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:sourceMD>"
    amd += '<mets:digiprovMD ID="rep1-amd-digiprov">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += "<dnx xmlns='http://www.exlibrisgroup.com/dps/dnx'/>"
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:digiprovMD>"
    amd += "</mets:amdSec>"
    return amd

def generate_mets_xml(ingest_data, storage_data):
    """
    main function to call to create the mets file. requires the ingest and the storage_data as json
    vars.
    """
    t_enriched = enrich_ingest_with_package_data(ingest_data, storage_data)
    t_flat_data = get_ingest_data_files(t_enriched)
    t_smap = generate_structmap(t_enriched)
    ie_dmd = generate_dmd_for_meta(t_enriched["metadata"], "ie-dmd", create_origin_uuid_metadata=False)
    mets_file = '<mets:mets xmlns:mets="http://www.exlibrisgroup.com/xsd/dps/rosettaMets">'
    file_dmd = ""
    file_amd = generate_amd_for_rep()
    file_sec = "<mets:fileSec>"
    file_sec += '<mets:fileGrp USE="VIEW" ID="f_grp_master" ADMID="rep1-amd">'
    for item in t_flat_data:
        package = [
            package
            for package in t_enriched["content"]
            if package["package_id"] == item["root_package"]
        ][0]
        for f in item["flat_data"]:
            file_ctr = ctr_id_map[f["package_id"]]
            file_sec += (
                '<mets:file ID="fid'
                + file_ctr
                + '-1" MIMETYPE="'
                + f["data_object_metadata"]["file_type"]
                + '" ADMID="fid' + file_ctr + '-1-amd"'

            )
            print("file_data")
            print(json.dumps(f))
            print("package")
            print(json.dumps(package))
            if "metadata_userset_id" in package and package["metadata_userset_id"] != "":
                #in case of upload it is nonsense to add a identifier, since it's not a managed repo
                result = {}
                if(f["data_object_metadata"]["content_origin"] == "upload"):
                    result = generate_dmd_for_meta(
                        package["metadata_userset"], "f_dmd_" + f["package_id"])
                else:
                    result = generate_dmd_for_meta(
                        package["metadata_userset"], "f_dmd_" + f["package_id"],True,\
                        f["data_object_metadata"]["content_origin"],\
                        f["data_object_metadata"]["origin_uuid"])
                if result["successfull"]:
                    file_dmd += result["content"]
                    file_sec += ' DMDID="f_dmd_' + f["package_id"] + '"'
            file_sec += '>'
            file_amd += generate_amd_for_file(
                f["data_object_metadata"], file_ctr
            )
            file_sec += (
                '<mets:FLocat LOCTYPE="URL" xlin:href="file://'
                + f["data_object_metadata"]["filename"]
                + '" xmlns:xlin="http://www.w3.org/1999/xlink"/>'
            )
            file_sec += "</mets:file>"
            #---
            #create the same for the json_meta file
            #---
            file_ctr = ctr_id_map[f["package_id"]+"_meta"]
            file_sec += (
                '<mets:file ID="fid'
                + file_ctr
                + '-1" MIMETYPE="'
                + f["data_object_metadata"]["file_type"]
                + '" ADMID="fid' + file_ctr + '-1-amd"'

            )
            file_sec += '>'
            meta = { 'filename' : f["data_object_metadata"]["filename"] \
                    + '.json' , 'file_type' : 'application/json'}
            file_amd += generate_amd_for_file(
                meta, file_ctr, generate_checksums=False
            )
            file_sec += (
                '<mets:FLocat LOCTYPE="URL" xlin:href="file://'
                + f["data_object_metadata"]["filename"] + '.json'
                + '" xmlns:xlin="http://www.w3.org/1999/xlink"/>'
            )
            file_sec += "</mets:file>"
    file_sec += "</mets:fileGrp>"
    file_sec += "</mets:fileSec>"
    mets_file += ie_dmd["content"]
    mets_file += file_dmd
    mets_file += file_amd
    mets_file += file_sec
    mets_file += t_smap
    mets_file += "</mets:mets>"
    return mets_file

if __name__ == "__main__":
    ingest_data = {}
    storage_data = {}
    with open("/server/lzv/server/testdata/test_ingest.json") as f:
        ingest_data = json.load(f)
    with open("/server/lzv/server/testdata/test_storage.json") as f:
        storage_data = json.load(f)
    mets = generate_mets_xml(ingest_data, storage_data)
    print(mets)
