from sanic.views import HTTPMethodView
from typing import Text, Optional, Dict
from sanic.response import json as sanic_response
from sanic import response

class BaseHandler(HTTPMethodView):
    def _send_response(self, 
                      status_code: int, 
                      success: Optional[bool]=True, 
                      response_msg: Optional[Text]=None, 
                      data: Optional[Dict]=None,
                      error_msg: Optional[Text]=None,
                      error_code: Optional[int]=None
                      ):
        if status_code == 200:
            response = {"success": success, "message": response_msg, "data": data}
        elif status_code == 404 or status_code == 400:
            response = {"success": success, "message": response_msg, "data": data}
        elif status_code == 500:
            response = {"success": False}
        if error_msg:
            response.update({
                "error_message": error_msg,
                "error_code": error_code
            })
        return sanic_response(response, status_code)

        

