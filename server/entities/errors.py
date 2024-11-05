class PathError(Exception):
    '''Path does not exist in filesystem'''

class ExportUserError(Exception):
    '''No export user configured'''

class OrganisationError(Exception):
    '''Organisation not found'''

class IdentityProviderError(Exception):
    '''Identity provider is missing information'''

class PatchError(Exception):
    '''Patch failed'''

class XMLValidationError(Exception):
    '''XML is invalid according to schema'''