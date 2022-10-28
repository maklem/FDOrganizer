from enum import Enum


class Databases(Enum):
    DOCUMENTS = 'documents'
    INGESTS = 'ingests'
    METADATA = 'metadata'
    REVIEW = 'ingest_review'
    STATIC = 'static'
    STORAGE = 'storage'
    ORGANISATIONS = 'organisations'
