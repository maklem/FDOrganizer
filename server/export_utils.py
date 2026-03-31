from typing import Any, Literal
import os
from datetime import datetime
from xmlschema import XMLSchema11
import jinja2

from .services.database import get
from .entities import Folder, Document, Package, Databases, Metadata
from .entities.errors import XMLValidationError

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

def create_structmap(entity: Package | Folder) -> dict[Literal['name','files','folders'],Any]:
    documents = [Document.from_db(get(Databases.DOCUMENTS, document_id).json()) for document_id in entity.documents]
    folders = [Folder.from_dict(get(Databases.FOLDERS, folder_id).json()) for folder_id in entity.folders]
    return {
        'name': entity.name,
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