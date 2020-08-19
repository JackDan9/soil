import uuid
import json
import threading

from oslo_log import log as logging
from requests import HTTPError
import requests

from soil.i18n import _, _LI, _LW, _LE
from soil.exception import SoilException
from soil.utils.log import get_request_id
import soil.conf


LOG = logging.getLogger(__name__)


CONF = soil.conf.CONF


request_state = threading.local()


def is_req_success(code):
    if code in (200, 201, 202, 204):
        return True
    return False


def post_request(url, body, token=None, no_resp_content=False):
    request_id = get_request_id()

    # if isinstance(body, dict):
    #     body = json.dumps(body)
    
    headers = {"Content-type": "application/json"}

    if token is not None:
        headers['X-Auth-Token'] = token
    
    post_info = "[%s] : curl -X POST '%s' -d '%s' %s" % (
        request_id, url, body, ' '.join([' -H "%s:%s"' % (key, value) for key, value in headers.items()])
    )

    try:
        LOG.info(_LI("Soil update request information: %(post_info)s"), 
                 {"post_info": post_info})
        response = requests.post(url=url, json=body, headers=headers)
    except HTTPError as he:
        LOG.error(_LE("Soil post request error information: '[%(request_id)s]' %(post_info)s ERROR: %(error_msg)s"), 
                  {"request_id": request_id, "post_info": post_info, "error_msg": he})
        raise SoilException(message=he)
    except Exception as e:
        LOG.exception(_LW("Soil post request exception information: '[%(request_id)s]' %(post_info)s EXCEPTION: %(e)s"), 
                      {"request_id": request_id, "post_info": post_info, "e": e})
        raise e
    
    code = response.status_code
    content = response.content

    if is_req_success(code=code):
        LOG.info(_LI("Soil post request success information: '[%(request_id)s]': RESP CODE: %(code)s, RESP DATA: %(content)s"), 
                 {"request_id": request_id, "code": code, "content": content})

        if no_resp_content:
            return
        return json.loads(content)
    
    LOG.error(_LE("Soil post request error information: '[%(request_id)s]' : RESP CODE : %(code)s, RESP DATA : %(content)s"), 
              {"request_id": request_id, "code": code, "content": content})
    raise SoilException(message=content)


def update_request(url, body, token=None, no_resp_content=False):
    request_id = get_request_id()

    if isinstance(body, dict):
        body = json.dumps(body)
    
    headers = {"Content-type": "application/json"}

    if token is not None:
        headers['X-Auth-Token'] = token
    
    put_info = "[%s] : curl -X PUT '%s' -d '%s' %s" % (
        request_id, url, body, ' '.join([' -H "%s:%s"' % (key, value) for key, value in headers.items()])
    )

    try:
        LOG.info(_LI("Soil update request information: %(put_info)s"), 
                 {"put_info": put_info})
        response = requests.put(url=url, json=body, headers=headers)
    except HTTPError as he:
        LOG.error(_LE("Soil update request error information: '[%(request_id)s]' %(put_info)s ERROR: %(error_msg)s"), 
                  {"request_id": request_id, "put_info": put_info, "error_msg": he})
        raise SoilException(message=he)
    except Exception as e:
        LOG.exception(_LW("Soil update request exception information: '[%(request_id)s]' %(put_info)s EXCEPTION: %(e)s"), 
                      {"request_id": request_id, "put_info": put_info, "e": e})
        raise e
    
    code = response.status_code
    content = response.content

    if is_req_success(code=code):
        LOG.info(_LI("Soil update request success information: '[%(request_id)s]': RESP CODE: %(code)s, RESP DATA: %(content)s"), 
                 {"request_id": request_id, "code": code, "content": content})

        if no_resp_content:
            return
        return json.loads(content)
    
    LOG.error(_LE("Soil update request error information: '[%(request_id)s]' : RESP CODE : %(code)s, RESP DATA : %(content)s"), 
              {"request_id": request_id, "code": code, "content": content})
    raise SoilException(message=content)


def get_request(url, token=None, body=None):
    request_id = get_request_id()
    
    headers = {"Content-type": "application/json"}

    if token is not None:
        headers['X-Auth-Token'] = token
    
    get_info = "[%s] : curl -X GET '%s' %s" % (
        request_id, url, ' '.join([' -H "%s:%s"' % (key, value) for key, value in headers.items()])
    )

    try:
        LOG.info(_LI("Soil get request information: %(get_info)s"), 
                 {"get_info": get_info})
        response = requests.get(url=url, headers=headers)
    except HTTPError as he:
        LOG.error(_LE("Soil get request error information: '[%(request_id)s]' %(get_info)s ERROR: %(error_msg)s"), 
                  {"request_id": request_id, "get_info": get_info, "error_msg": he})
        raise SoilException(message=he)
    except Exception as e:
        LOG.exception(_LW("Soil get request exception information: '[%(request_id)s]' %(get_info)s EXCEPTION: %(e)s"), 
                      {"request_id": request_id, "get_info": get_info, "e": e})
        raise e
    
    code = response.status_code
    content = response.content

    if is_req_success(code=code):
        LOG.info(_LI("Soil get request success information: '[%(request_id)s]': RESP CODE: %(code)s, RESP DATA: %(content)s"), 
                 {"request_id": request_id, "code": code, "content": content})
        return json.loads(content)
    
    LOG.error(_LE("Soil get request error information: '[%(request_id)s]' : RESP CODE : %(code)s, RESP DATA : %(content)s"), 
              {"request_id": request_id, "code": code, "content": content})
    raise SoilException(message=content)


def delete_request(url, token=None, body=None):
    request_id = get_request_id()
    
    headers = {"Content-type": "application/json"}

    if token is not None:
        headers['X-Auth-Token'] = token
    
    delete_info = "[%s] : curl -X DELETE '%s' %s" % (
        request_id, url, ' '.join([' -H "%s:%s"' % (key, value) for key, value in headers.items()])
    )

    try:
        LOG.info(_LI("Soil delete request information: %(delete_info)s"), 
                 {"post_info": delete_info})
        response = requests.post(url=url, json=body, headers=headers)
    except HTTPError as he:
        LOG.error(_LE("Soil delete request error information: '[%(request_id)s]' %(delete_info)s ERROR: %(error_msg)s"), 
                  {"request_id": request_id, "delete_info": delete_info, "error_msg": he})
        raise SoilException(message=he)
    except Exception as e:
        LOG.exception(_LW("Soil delete request exception information: '[%(request_id)s]' %(delete_info)s EXCEPTION: %(e)s"), 
                      {"request_id": request_id, "delete_info": delete_info, "e": e})
        raise e
    
    code = response.status_code
    content = response.content

    if is_req_success(code=code):
        LOG.info(_LI("Soil delete request success information: '[%(request_id)s]': RESP CODE: %(code)s, RESP DATA: %(content)s"), 
                 {"request_id": request_id, "code": code, "content": content})
        return json.loads(content)
    
    LOG.error(_LE("Soil delete request error information: '[%(request_id)s]' : RESP CODE : %(code)s, RESP DATA : %(content)s"), 
              {"request_id": request_id, "code": code, "content": content})
    raise SoilException(message=content)