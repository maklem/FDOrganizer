from typing import Any, Literal, TypedDict, Optional
import os
from datetime import datetime
from xmlschema import XMLSchema11
import jinja2

from .services.database import get
from .entities import Folder, Document, Package, Databases, Metadata
from .entities.errors import XMLValidationError

StructMap = TypedDict('StructMap', {
    'name': str,
    'metadata': Optional[str],
    'folders': list['StructMap'],
    'files': list[Document],
})

def timestamp_to_date(value, format="%Y-%m-%d"):
    return datetime.fromtimestamp(value / 1000).strftime(format)

def create_package_data(package: Package) -> dict[Literal['metadata','id'],Any]:
    if package.metadata is None:
        raise ValueError('Package has no metadata')
    metadata = Metadata.from_dict(get(Databases.METADATA, package.metadata).json())
    return {
        'metadata': metadata.metadata,
        'id': package.id
    }

def check_languages(languages: list[dict[str,Any]], filename) -> list[str]:
    errors: list[str] = []

    for i in range(len(languages)):
        error_prefix = f"In metadata for \"{filename}\": language[{i}]"
        if "languageType" not in languages[i]:
            errors.append(f"{error_prefix} has no type.")
            continue
        if languages[i]["languageType"][0] == "naturalLanguage":
            if "languageCode" not in languages[i]:
                errors.append(f"{error_prefix} of type 'naturalLanguage' has no languageCode.")
                continue
            if languages[i]["languageCode"][0] == "custom":
                if "customLanguage" not in languages[i]:
                    errors.append(f"{error_prefix} of type 'naturalLanguage' with code 'custom' has no custom value.")
                    continue
        elif languages[i]["languageType"][0] == "programmingLanguage":
            if "customProgrammingLanguage" not in languages[i]:
                errors.append(f"{error_prefix} of type 'programmingLanguage' has no value.")
                continue
        else:
            errors.append(f"{error_prefix} has unknown type.")
            continue
    return errors

def check_document(prefix: str, document: Document) -> list[str]:
    errors = []
    if document.metadata is not None:
        metadata = Metadata.from_dict(get(Databases.METADATA, document.metadata).json())
        if "language" in metadata.metadata:
            errors = check_languages(metadata.metadata["language"], os.path.join(prefix, document.name))
    return errors

def check_folder(prefix: str, folder: StructMap) -> list[str]:
    errors = []
    if "metadata" in folder and folder["metadata"] is not None:
        metadata = Metadata.from_dict(get(Databases.METADATA, folder["metadata"]).json())
        if "language" in metadata.metadata:
            errors = check_languages(metadata.metadata["language"], os.path.join(prefix, folder["name"]))
    return errors

def check_structmap(prefix, structmap:StructMap) -> list[str]:
    errors = []
    for e in check_folder(prefix, structmap):
        errors.append(e)    

    current_prefix = os.path.join(prefix, structmap["name"])
    for file in structmap['files']:
        for e in check_document(current_prefix, file):
            errors.append(e)
    for folder in structmap['folders']:
        for e in check_structmap(current_prefix, folder):
            errors.append(e)
    return errors

def create_structmap(entity: Package | Folder) -> StructMap:
    documents = [Document.from_db(get(Databases.DOCUMENTS, document_id).json()) for document_id in entity.documents]
    folders = [Folder.from_dict(get(Databases.FOLDERS, folder_id).json()) for folder_id in entity.folders]
    return {
        'name': entity.name,
        'metadata': entity.metadata,
        'files': documents,
        'folders': [create_structmap(folder) for folder in folders]
    }

def build_sip_metadata(package_data, file_list, structmap) -> str:
    templateLoader = jinja2.FileSystemLoader(searchpath=[os.path.join('server', 'metadata_templates', 'rosetta-mets'), os.path.join('server', 'metadata_templates', 'dublincore')])
    templateEnv = jinja2.Environment(
        loader=templateLoader,
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True
    )
    templateEnv.filters["timestamp_to_date"] = timestamp_to_date
    template = templateEnv.get_template('rosetta-mets.xml.jinja')
    rendered_xml = template.render(files = file_list, package = package_data, structmap = structmap)
    schema_path = os.path.join('server', 'metadata_templates', 'rosetta-mets', 'schema')
    schema_file = open(os.path.join(schema_path, 'rosetta-mets_7.3.xsd'))
    schema = XMLSchema11(schema_file, base_url=schema_path)
    try:
        schema.validate(rendered_xml)
    except Exception as error:
        raise XMLValidationError(f'Validation of METS-File failed: {error.args[0]}', rendered_xml)
    return rendered_xml

def add_label(metadata: Metadata):
    try:
        return metadata.metadata['title'][0]['titleText'][0]
    except KeyError:
        return ""
    
def add_note(metadata: Metadata):
    try:
        notes = [description['textAbstract'] for description in metadata.metadata['description'] if description['descriptionType'][0] == "descriptionAbstract"]
        if notes:
            return notes[0]
        else:
            return ""
    except KeyError:
        return ""
