import mimetypes


class File(object):
    filename: str = None
    filetype: str = None
    location: str = None

    def __init__(self, filename, location):
        self.location = location
        self.filetype = mimetypes.MimeTypes().guess_type(location)[0]
        self.filename = '{}{}'.format(filename, mimetypes.MimeTypes().guess_extension(self.filetype))
