from api.base_handler import BaseHandler
from sanic.response import json as sanic_json
from sanic import response
from typing import Dict, Text
from db.models import Url
from validations.validate import UrlSchema
from db.connection import get_session
from api.decorators import is_authorized, check_existing_url, check_file
from sanic.log import logger
import os
from api.helper import create_file_path, write_to_file
import json
from common.constants import HTTP_500, HTTP_200, HTTP_404

default_folder_name: Text = 'uploads'

class UploadFileHandler(BaseHandler):
    @is_authorized
    @check_existing_url()
    @check_file
    async def post(self, request, *args, **kwargs):
        """Upload file handler.
        
        This handler uploads file in the server against given url.
        Uses Auth to authorize request.
        Args: 
            request (object): Sanic request object.
        
        Returns:
            json:
                id: int.
        """
        try:
            data: Dict = request.form
            folder_name: Text = data.get("folder", default_folder_name)
            identifier: Text = data.get("identifier")
            url: Text = data.get("url")
            method: Text = str(data.get("method")).upper()
            body: Dict = json.loads(data.get("body", {}))
            response: Dict = json.loads(data.get("response", {}))
            headers: Dict = json.loads(data.get("headers", {}))
            status_code: int = data.get("status_code")
            execute: bool = json.loads(data.get("execute"))
            file_obj: object = request.files.get("file")
            filename: Text = file_obj.name
            logger.info({
                "folder_name": folder_name,
                "identifier": identifier,
                "url": url,
                "method": method,
                "body": body,
                "response": response,
                "headers": headers,
                "status_code": status_code,
                "execute": execute,
                "filename": filename
            })
            filepath: Text = await create_file_path(filename, foldername=folder_name)
        except Exception as ex:
            logger.exception(f"UploadFileHandler, POST, error: {ex}")
            self._send_response(HTTP_500, False, error_msg=ex)
        logger.info("UploadFileHandler, POST, getting session.")
        session = get_session()
        try:
            url_data = {
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
            logger.info(f"UploadFileHandler, POST, url_data: {url_data}")
            error: object = UrlSchema().validate(url_data)
            if error:
                logger.error(f"UploadFileHandler, POST, error: {error}")
                return self._send_response(HTTP_500, success=False, error_code=HTTP_500, error_msg=error)
            url_obj: Url = Url(**url_data)
            session.add(url_obj)
            logger.info("UploadFileHandler, POST, created url in the database.")
            session.commit()
            logger.info(f"UploadFileHandler, POST, writing file to the filepath: {filepath}")
            await write_to_file(filepath, file_obj)
            return self._send_response(HTTP_200, response_msg="url created", data={"url_id": url_obj.id})
        except Exception as exe:
            logger.exception(f"UploadFileHandler, POST, error: {exe}")
            session.rollback()
            return self._send_response(HTTP_500, success=False, error_code=HTTP_500, error_msg=exe)
        finally:
            logger.info("UploadFileHandler, POST, closing session.")
            session.close()

class UrlHandler(BaseHandler):
    @is_authorized
    @check_existing_url(json_format=True)
    async def post(self, request, *args, **kwargs):
        """Upload file handler.
        
        This handler creates json data in the database against given url.
        Uses Auth to authorize request.
        Args: 
            request (object): Sanic request object.
        
        Returns:
            json:
                id: int.
        """
        data: Dict = request.json
        identifier: Text = data.get("identifier")
        url: Text = data.get("url")
        method: Text = str(data.get("method")).upper()
        body: Dict = data.get("body", {})
        response: Dict = data.get("response", {})
        headers: Dict = data.get("headers", {})
        status_code: int = data.get("status_code")
        logger.info("AddUrlHandler, POST, getting session.")
        session = get_session()
        try:
            url_data = {
                "identifier": identifier,
                "url": url,
                "method": method,
                "body": body,
                "response": response,
                "headers": headers,
                "status_code": status_code,
                "execute": False
            }
            error: object = UrlSchema().validate(url_data)
            if error:
                logger.error(f"AddUrlHandler, POST, error: {error}")
                return self._send_response(HTTP_500, success=False, error_code=HTTP_500, error_msg=error)
            url_obj: Url = Url(**url_data)
            session.add(url_obj)
            logger.info("AddUrlHandler, POST, added url in the database.")
            session.commit()
            return self._send_response(HTTP_200, response_msg="url created", data={"url_id": url_obj.id})
        except Exception as exe:
            logger.exception(f"AddUrlHandler, POST, error: {exe}")
            session.rollback()
            return self._send_response(HTTP_500, success=False, error_code=HTTP_500, error_msg=exe)
        finally:
            logger.info("AddUrlHandler, POST, closing session.")
            session.close()

    @is_authorized
    async def get(self, request, *args, **kwargs):
        logger.info("UrlHandler, GET, getting session.")
        session = get_session()
        try:
            args: Dict = request.args
            logger.info(f"UrlHandler, GET, request arguments: {args}")
            if args.get("url_id", None):
                url_ids: list = args["url_id"]
                url_objs: list = session.query(Url).filter(Url.id.in_(url_ids)).all()
            elif args.get("identifier", None):
                identifiers: list = args["identifier"]
                url_objs : list= session.query(Url).filter(Url.identifier.in_(identifiers)).all()
            else:
                url_objs: list = session.query(Url).all()
            if not url_objs:
                return self._send_response(HTTP_404, response_msg="no url found", data=[])
            urls: list = []
            for url_obj in url_objs:
                url_json: object = UrlSchema(only=["id", "identifier", "url", "method", "status_code", "execute"]).dump(url_obj)
                urls.append(url_json)
            return self._send_response(HTTP_200, data=urls)
        except Exception as exe:
            logger.exception(f"UrlHandler, GET, exception: {exe}")
            session.rollback()
            return self._send_response(HTTP_500, success=False, error_code=HTTP_500, error_msg=exe)
        finally:
            logger.info("UrlHandler, GET, closing session.")
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

