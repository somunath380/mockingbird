from typing import Dict, Text
from db.models import Url
import os
from sanic.response import json as sanic_json
from sanic.log import logger
from db.connection import get_session
from functools import wraps
from common.constants import HTTP_401, HTTP_403, HTTP_404, MAX_FILE_SIZE
from api.helper import create_basedir


def is_authorized(func):
    """Middleware to check if the request is authorized for processing.
    Args: 
        None.
    Returns:
        Sanic Response object or Handler Function.
    """
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        try:
            auth_header: Text = request.headers.get("Authorization", None)
            if auth_header is None:
                logger.info("is_authorized, Invalid Authorization")
                return sanic_json({"status": False, "message": "Invalid Authorization"}, HTTP_401)
            api_auth: Text = auth_header[7:]
            print(os.environ.get("API_AUTH"))
            if api_auth != os.environ.get("API_AUTH"):
                logger.info("is_authorized, Invalid Authorization")
                return sanic_json({"status": False, "message": "Invalid Authorization"}, HTTP_401)
            else:
                logger.info("is_authorized, Connection Authorized.")
                return await func(self, request, *args, **kwargs)
        except Exception as exe:
            logger.error(f"is_authorized, error occured {exe}")
            return sanic_json({"status": False, "message": "Invalid Authentication", "error": exe}, HTTP_403)
    return wrapper


def check_existing_url(json_format):
    """Middleware to check if the url already exists or not.
    Args:
        json_format (bool): Default False.
    Returns:
        Sanic Response object or Handler Function.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, request, *args, **kwargs):
            if json_format:
                url_identifier: Text = request.json.get("identifier")
                request_url: Text = request.json.get("url")
            else:
                url_identifier: Text = request.form.get("identifier")
                request_url: Text = request.form.get("url")
            logger.info(f"check_existing_url, url_identifier: {url_identifier}")
            if not url_identifier:
                return sanic_json({"status": False, "message": "URL Identifier required"}, HTTP_403)
            if not request_url:
                return sanic_json({"status": False, "message": "URL required"}, HTTP_403)
            session: object = get_session()
            try:
                url_obj: object = session.query(Url).filter(Url.identifier==url_identifier).first()
                if url_obj:
                    return sanic_json({"status": False, "message": "given URL with identifier {} already exists!".format(url_identifier)}, HTTP_403)
                url_obj: object = session.query(Url).filter(Url.url==request_url).first()
                if url_obj:
                    return sanic_json({"status": False, "message": "given URL {} already exists!".format(request_url)}, HTTP_403)
                return await func(self, request, *args, **kwargs)
            except Exception as exe:
                logger.error(f"check_existing_url, error: {exe}")
                session.rollback()
                return sanic_json({"status": False, "message": "Invalid Authentication", "error": exe}, HTTP_403)
            finally:
                logger.info("check_existing_url, closing session")
                session.close()
        return wrapper
    return decorator


def check_file(func):
    """Middleware to check file object that is being uploaded.
    Args: 
        None.
    Returns:
        Sanic Response object or Handler Function.
    """
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        file_obj: object = request.files.get("file")
        filename: Text = file_obj.name
        if not filename:
            return sanic_json({"status": False, "message": "File required"}, HTTP_401)
        if len(os.path.splitext(filename)[0]) > 15:
            return sanic_json({"status": False, "message": "File name length must be below 15 characters"}, HTTP_401)
        logger.info(f"check_file, filename: {filename}")
        basedir: Text = await create_basedir()
        logger.info(f"check_file, basedir: {basedir}")
        filepath = os.path.join(basedir, "uploads", filename)
        if os.path.exists(filepath):
            logger.info(f"check_file, file with given name {filename} already exists")
            return sanic_json({"status": False, "message": f"file with given name {filename} already exists"}, HTTP_401)
        file_name, file_extension = os.path.splitext(filepath)
        logger.info(f"check_file, file extension: {file_extension}")
        allowed_extensions = [".py", ".pdf"]
        if file_extension not in allowed_extensions:
            return sanic_json({"status": False, "message": f"only {allowed_extensions} files allowed"}, HTTP_401)
        if len(file_obj.body) <= 0 or len(file_obj.body) >= MAX_FILE_SIZE:
            return sanic_json({"status": False, "message": "file size too large"}, HTTP_401)
        return await func(self, request, *args, **kwargs)
    return wrapper

def get_url(func):
    """Middleware to get url object.
    Args: 
        None.
    Returns:
        Sanic Response object or Handler Function.
    """
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        # get url object using the url_id or url_identifier given in request
        data: Dict = request.json
        url_id: int = data.get("id", None)
        if url_id is None:
            return sanic_json("url id required", HTTP_401)
        # get the url obj from the db
        session = get_session()
        try:
            url_obj = session.query(Url).filter(Url.id==url_id).first()
            if not url_obj:
                return sanic_json({"no url found"}, HTTP_404)
            kwargs["url_obj"] = url_obj
            return await func(self, request, *args, **kwargs)
        except Exception as exe:
            logger.exception(f"get_url, error occured, exception {exe}")
            session.rollback()
        finally:
            session.close()
    return wrapper


