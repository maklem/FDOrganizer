"""
Module for creation of mets files.
"""
import json

allowed_metadata_identifer = ["dublin_core_1_1"]




def enrich_ingest_with_package_data(ingest, storage_file):
    """
    recursivly enhances the packages data by replacing in "content.child_data_objects" the id
    with new json objects containing the actual file information. This is expected to be done
    before creating the export xml string to simplify processing. expects the ingest, returns
    json object.
    """
    print("storage file")
    print(storage_file)
    print("base ingest:")
    print(ingest)
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
        print("content:")
        print(content)
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
    smap = '<structMap Type="Logical">'
    smap += '<div ID="' + ingest["ingest_id"] + '" LABEL="' + ingest["name"] + '">'
    for con in ingest["content"]:
        smap += (
            '<div ID="'
            + con["package_id"]
            + '" LABEL="'
            + con["package_data"]["name"]
            + '">'
        )
        for item in con["package_data"]["child_data_objects"]:
            smap += rec_gen_smap(item)
        smap += "</div>"
    smap += "</div>"
    smap += "</structMap>"
    return smap


def rec_gen_smap(package):
    """
    recursively generates the structmap data
    """
    smap = ""
    if package["type"] == "DATA":
        smap += '<fptr FILEID="' + package["package_id"] + '"/>'
    else:
        smap += (
            '<div ID="' + package["package_id"] + '" LABEL="' + package["name"] + '">'
        )
        for item in package["child_data_objects"]:
            smap += rec_gen_smap(item)
        smap += "</div>"
    return smap


def generate_dmd_for_meta(file_meta, identifier):
    """
    generate a dmd for each file. only required if package containing file has additional
    metadata set to in ingest.
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
    dmd += "</dc:record>"
    dmd += "</mets:xmlData>"
    dmd += "</mets:mdWrap>"
    dmd += "</mets:dmdSec>"
    return {"successfull": True, "content": dmd}


# def generate_dmd_for_ingest(ingest_meta):
#     '''
#     generate a dmd for the ingest. based on the metadata set in the root ingest.
#     return this as xml string. This is basically the same as the function above, resuse that.
#     '''
#     dmd = ''
#     dmd += '<mets:dmdSec ID="ie-dmd">'
#     dmd += '<mets:mdWrap MDTYPE="DC">'
#     dmd += '<mets:xmlData>'
#     dmd += '<dc:record xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
#     dmd += <dc:creator>Exlibris</dc:creator>
#     dmd += <dc:identifier>ISBN 1-56389-016-X</dc:identifier>
#     dmd += <dc:title>SDK - TEST DC</dc:title>
#     dmd += '</dc:record>'
#     dmd += '</mets:xmlData>'
#     dmd += '</mets:mdWrap>'
#     dmd += '</mets:dmdSec>'
#     return dmd


def generate_amd_for_file(amd_meta, identifier):
    """
    generate a techMD section with repository specific metadata:
    amd_meta in structure:
    {"section1" : {"metafield" : "metavalue"}, "section2":{"metafield": "value"}, ...}
    return this as xml string.
    """
    amd = ""
    amd += '<mets:amdSec ID="f_amd_' + identifier + '">'
    amd += '<mets:techMD ID="f_techmd_' + identifier + '">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx">'
    for sec_key in amd_meta:
        amd += '<section id="' + sec_key + '">'
        amd += "<record>"
        for key in amd_meta[sec_key]:
            amd += '<key id="' + key + '">' + str(amd_meta[sec_key][key]) + "</key>"
        amd += "</record>"
        amd += "</section>"
    amd += "</dnx>"
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:techMD>"
    amd += '<mets:rightsMD ID="f_rightsmd_' + identifier + '">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx"/>'
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:rightsMD>"
    amd += '<mets:sourceMD ID="f_sourcemd_' + identifier + '">'
    amd += '<mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="dnx">'
    amd += "<mets:xmlData>"
    amd += '<dnx xmlns="http://www.exlibrisgroup.com/dps/dnx"/>'
    amd += "</mets:xmlData>"
    amd += "</mets:mdWrap>"
    amd += "</mets:sourceMD>"
    amd += '<mets:digiprovMD ID="f_digiprovmd_' + identifier + '">'
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
    ie_dmd = generate_dmd_for_meta(t_enriched["metadata"], "ie_dmd")
    mets_file = '<mets:mets xmlns:mets="http://www.loc.gov/METS/">'
    file_dmd = ""
    file_amd = ""
    file_sec = "<mets:fileSec>"
    for item in t_flat_data:
        package = [
            package
            for package in t_enriched["content"]
            if package["package_id"] == item["root_package"]
        ][0]
        for f in item["flat_data"]:
            file_sec += '<mets:fileGrp USE="VIEW">'
            file_sec += (
                '<mets:file ID="'
                + f["package_id"]
                + '" MIMETYPE="'
                + f["data_object_metadata"]["file_type"]
                + '" ADMID="f_amd_'
                + f["package_id"]
                + '" DMDID="f_dmd_'
                + f["package_id"]
                + '">'
            )
            if "metadata_userset_id" in package:
                result = generate_dmd_for_meta(
                    package["metadata_userset"], "f_dmd_" + f["package_id"]
                )
                if result["successfull"]:
                    file_dmd += result["content"]
            section_data = {"export_metadata": f["data_object_metadata"]}
            if bool(f["origin_metadata"]):
                section_data[
                    f["data_object_metadata"]["content_origin"] + "_metadata"
                ] = f["origin_metadata"]
            file_amd += generate_amd_for_file(
                section_data, f["package_id"]
            )
            file_sec += (
                '<mets:FLocat LOCTYPE="URL" xlin:href="file://'
                + f["data_object_metadata"]["filename"]
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
