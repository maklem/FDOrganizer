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

class PluginError(Exception):
    '''Plugin failed'''
    def __init__(self, plugin: str, status_code: int, message: str):
        self.plugin = plugin
        self.status_code = status_code
        self.message = message
        self.text = plugin + " has produced an error: Status code " + str(status_code) + "; " + message
        self.add_note(self.text)

