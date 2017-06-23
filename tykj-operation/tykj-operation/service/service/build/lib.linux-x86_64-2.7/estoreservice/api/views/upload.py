import os
import logging
import random
from django.conf import settings
from estorecore.servemodels.upload import UploadMongodbStorage
from estoreservice.decorators import exception_handled
from estoreservice.utils.utils import json_response_ok, json_response_error
from estoreservice.utils.resp_code import PARAM_REQUIRED, SAVE_FILE_ERROR
from estoreservice.utils import date_today, unix_time
from estoreservice.settings import UPLOAD_ROOT, UPLOAD_FILE_TYPE

logger = logging.getLogger('estoreservice')

upload_db = UploadMongodbStorage(settings.MONGODB_CONF)


def generate_file_path(package):
    udir = os.path.join(UPLOAD_ROOT, package, date_today(package))
    if not os.path.exists(udir):
        os.makedirs(udir)
    while True:
        name = '%s%s' % (str(unix_time())[2:],
                         str(random.randint(10000, 99999)))
        fpath = '%s.%s' % (name, UPLOAD_FILE_TYPE)
        if not os.path.exists(fpath):
            break
    return os.path.join(udir, fpath)


@exception_handled
def crash_report(request):
    '''
    Update the report file
    Multipart POST parameters:
        package: package name and version

    Return:
    {
        "status": 0,
        "data": {
        }
    }
    '''
    post = request.POST
    package = post.get('package')

    if not package or 'report' not in request.FILES:
        return json_response_error(PARAM_REQUIRED, 'Parameters is not valid')

    snippet_file = request.FILES['report']

    # use +8 timezone for all counts
    upload_db.count_crash(date_today(''))

    try:
        fpath = generate_file_path(package)
    except Exception as e:
        logger.error('SAVE_FILE_ERROR - Check dir failed with exception %s', e)
        return json_response_error(SAVE_FILE_ERROR, 'Save failed')

    audio_file = open(fpath, 'wb')
    try:
        for chunk in snippet_file.chunks():
            audio_file.write(chunk)
    except Exception as e:
        logger.error(
            'SAVE_FILE_ERROR - Write report file failed with exception %s',
            e)
        return json_response_error(SAVE_FILE_ERROR, 'Save failed')
    finally:
        audio_file.close()

    return json_response_ok()
