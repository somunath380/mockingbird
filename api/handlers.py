from api.base_handler import BaseHandler
from sanic.response import json as sanic_json
from sanic import response
from typing import Dict, List
from db.models import Url, User
from validations.validate import UserSchema, UrlSchema
from api.helper import encrypt_pwd
from db.connection import get_session
from api.decorators import check_existing_user, is_authorized, check_existing_url, is_admin
from sanic.log import logger
import os
from api.helper import create_file_path, write_to_file
import json

default_folder_name = 'uploads'

class UserView(BaseHandler):

    @is_authorized
    async def get(self, request, *args, **kwargs):
        """Get user details handler.
        
        This handler returns all existing users data by taking user_id or username
        given in the request params. Uses Basic Auth to authorize request.

        Args: 
            request (object): request object received.
        
        Returns:
            json: 
                username: str
                id: int.
        """
        session = get_session()
        try:
            args: Dict = request.args
            if args.get("user_id", None):
                ids: List = args["user_id"]
                user_objs = session.query(User).filter(User.id.in_(ids)).all()
            elif args.get("username", None):
                username: List = args["username"]
                user_objs = session.query(User).filter(User.username.in_(username)).all()
            else:
                user_objs = session.query(User).all()
            if not user_objs:
                return self._send_response(404, response_msg="no user found", data=[])
            users: List = []
            for user_obj in user_objs:
                user_json = UserSchema(only=["id", "username"]).dump(user_obj)
                users.append(user_json)
            return self._send_response(200, data=users)
        except Exception as exe:
            session.rollback()
            return self._send_response(500, success=False, error_code=500, error_msg=exe)
        finally:
            session.close()
    
    @is_authorized
    async def delete(self, request, *args, **kwargs):
        """Delete user details handler.
        
        This handler deletes specified users data by taking username
        from the authorization. Uses Basic Auth to authorize request.

        Args: 
            request (object): request object received.
        
        Returns:
            json.
        """
        session = get_session()
        try:
            username = kwargs.get("username")
            session.query(User).filter(User.username == username).delete()
            session.commit()
            return self._send_response(200, True, "user deleted")
        except Exception as exe:
            session.rollback()
            return self._send_response(500, success=False, error_code=500, error_msg=exe)
        finally:
            session.close()

class RegisterUser(BaseHandler):
    @check_existing_user
    async def post(self, request):
        """Create user handler.
        
        This handler will create new user.
        
        Args:
            request"""
        session = get_session()
        try:
            data: Dict = request.json
            error = UserSchema().validate(data)
            if error:
                return self._send_response(500, success=False, error_code=500, error_msg=error)
            secret = await encrypt_pwd(data)
            data["password"] = secret
            user_obj = User(**data)
            session.add(user_obj)
            session.commit()
            return self._send_response(200, response_msg="user created", data={"user_id": user_obj.id})
        except Exception as exe:
            session.rollback()
            return self._send_response(500, success=False, error_code=500, error_msg=exe)
        finally:
            session.close()

class UploadFileHandler(BaseHandler):
    @is_authorized
    @check_existing_url()
    async def post(self, request, *args, **kwargs):
        """Upload file handler.
        
        This handler uploads file in the server against given url.
        Uses Basic Auth to authorize request.
        Args: 
            request (object): request object received.
        
        Returns:
            json: 
                username: str
                id: int.
        """
        try:
            user_id = kwargs.get("id")
            data = request.form
            folder_name = data.get("folder", default_folder_name)
            identifier = data.get("identifier")
            url = data.get("url")
            method = str(data.get("method")).upper()
            body = json.loads(data.get("body", {}))
            response = json.loads(data.get("response", {}))
            headers = json.loads(data.get("headers", {}))
            status_code = data.get("status_code")
            execute = json.loads(data.get("execute"))
            file_obj = request.files.get("file")
            filename = file_obj.name

            filepath = await create_file_path(filename, foldername=folder_name)
        except Exception as ex:
            self._send_response(500, False, error_msg=ex)
        session = get_session()
        try:
            url_data = {
                "user_id": user_id,
                "identifier": identifier,
                "filepath": filepath,
                "url": url,
                "method": method,
                "body": body,
                "response": response,
                "headers": headers,
                "status_code": status_code,
                "execute": execute
            }
            error = UrlSchema().validate(url_data)
            if error:
                return self._send_response(500, success=False, error_code=500, error_msg=error)
            url_obj = Url(**url_data)
            session.add(url_obj)
            session.commit()
            await write_to_file(filepath, file_obj)
            return self._send_response(200, response_msg="url created", data={"url_id": url_obj.id})
        except Exception as exe:
            session.rollback()
            return self._send_response(500, success=False, error_code=500, error_msg=exe)
        finally:
            session.close()

    @is_authorized
    @is_admin
    async def delete(self, request, *args, **kwargs):
        files = os.path.join(os.getcwd(), 'files')
        os.system(f'rm -rf {files}')
        return self._send_response(200, True, response_msg="server storage for all files deleted")

class AddUrlHandler(BaseHandler):
    @is_authorized
    @check_existing_url(json_format=True)
    async def post(self, request, *args, **kwargs):
        user_id = kwargs.get("id")
        data = request.json
        identifier = data.get("identifier")
        url = data.get("url")
        method = str(data.get("method")).upper()
        body = data.get("body", {})
        response = data.get("response", {})
        headers = data.get("headers", {})
        status_code = data.get("status_code")
        session = get_session()
        try:
            url_data = {
                "user_id": user_id,
                "identifier": identifier,
                "url": url,
                "method": method,
                "body": body,
                "response": response,
                "headers": headers,
                "status_code": status_code,
                "execute": False
            }
            error = UrlSchema().validate(url_data)
            if error:
                print(error)
                return self._send_response(500, success=False, error_code=500, error_msg=error)
            url_obj = Url(**url_data)
            session.add(url_obj)
            session.commit()
            return self._send_response(200, response_msg="url created", data={"url_id": url_obj.id})
        except Exception as exe:
            session.rollback()
            return self._send_response(500, success=False, error_code=500, error_msg=exe)
        finally:
            session.close()

class GetUrlHandler(BaseHandler):
    @is_authorized
    async def get(self, request, *args, **kwargs):
        session = get_session()
        try:
            args: Dict = request.args
            if args.get("url_id", None):
                url_ids = args["url_id"]
                url_objs = session.query(Url).filter(Url.id.in_(url_ids)).all()
            elif args.get("identifier", None):
                identifiers = args["identifier"]
                url_objs = session.query(Url).filter(Url.identifier.in_(identifiers)).all()
            else:
                url_objs = session.query(Url).all()
            if not url_objs:
                return self._send_response(404, response_msg="no url found", data=[])
            urls = []
            for url_obj in url_objs:
                url_json = UrlSchema(only=["id", "identifier", "url", "method", "status_code", "execute"]).dump(url_obj)
                urls.append(url_json)
            return self._send_response(200, data=urls)
        except Exception as exe:
            session.rollback()
            return self._send_response(500, success=False, error_code=500, error_msg=exe)
        finally:
            session.close()
    
    @is_authorized
    async def delete(self, request, *args, **kwargs):
        session = get_session()
        try:
            url_id = request.args.get("url_id", None)
            if url_id is None:
                return self._send_response(400, False, "url_id is required")
            url = session.query(Url).filter(Url.id == url_id).first()
            if not url:
                return self._send_response(404, False, "no url found")
            session.query(Url).filter(Url.id == url_id).delete()
            session.commit()
            return self._send_response(200, True, f"url id {url_id} deleted")
        except Exception as exe:
            session.rollback()
            return self._send_response(500, success=False, error_code=500, error_msg=exe)
        finally:
            session.close()

async def handle_request(request, path):
    session = get_session()
    try:
        url_obj = session.query(Url).filter(Url.url == path).first()
        # If url path is not stored in db
        if not url_obj:
            return sanic_json({"success": False, "message": "no url found"}, 404)
        # if url path is stored in db
        method = url_obj.method
        # if request method doesn't match the method in db
        if method != request.method:
            return sanic_json({"success": False, "message": "url does not support {} method".format(request.method)}, 400)
        # if no filepath is stored in db then its a normal json response
        if not url_obj.filepath:
            return sanic_json(url_obj.response, 200, headers={"Content-type": "application/json"})
        # if execute is false then its a file to be responsed
        if not url_obj.execute:
            filepath = os.path.join(os.getcwd(), url_obj.filepath)
            cwd = os.getcwd()
            response_filepath = filepath.replace(cwd+'/files', '')
            response_headers = {
                    "Content-Disposition": f'Attachment; filename="{response_filepath}"',
                    "Content-Type": "application/json",
                }
            if request.headers.get("Content-type") == "application/pdf":
                response_headers["Content-Type"] = "application/pdf"
            return await response.file_stream(
                filepath,
                chunk_size=1024,
                # mime_type="application/metalink4+xml",
                headers=response_headers
            )
        
    except Exception as ex:
        session.rollback()
        return sanic_json({"success": False, "error_msg": ex})
    finally:
        session.close()

