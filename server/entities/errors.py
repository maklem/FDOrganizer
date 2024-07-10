class PathError(Exception):
    '''Path does not exist in filesystem'''

class ExportUserError(Exception):
    '''No export user configured'''