from validations.validate import UserSchema
from typing import Dict, Text
from db.models import User, Url
from sanic.response import json
import base64
from api.helper import encrypt_pwd
from db.connection import get_session

def check_user():
    def outer_wrapper(f):
        async def wrapper(request, *args, **kwargs):
            session = get_session()
            try:
                request_data: Dict = request.json
                request_data = UserSchema().load(request_data)
                username: Text = request_data.get("username")
                user_obj = session.query(User).filter(User.username == username).first()
                if user_obj:
                    return json({"status": False, "message": "user with username {} already exists".format(username)})
                return await f(request, *args, **kwargs)
            except Exception:
                session.rollback()
            finally:
                session.close()
        return wrapper
    return outer_wrapper

def is_authorized():
    def outer_wrapper(f):
        async def wrapper(request, *args, **kwargs):
            session = get_session()
            try:
                auth_header = request.headers.get("Authorization")
                if auth_header is None:
                    return json({"status": False, "message": "unable to Authorize"}, 400)
                auth_decoded = base64.b64decode(auth_header[6:]).decode()
                username, password = auth_decoded.split(":")
                user_obj = session.query(User).filter(User.username == username).first()
                if user_obj:
                    db_pwd = user_obj.password
                    encrypted_pwd = await encrypt_pwd(user_details={"username":username, "password":password})
                    if encrypted_pwd == db_pwd:
                        kwargs.update(
                            {
                                "id": user_obj.id,
                                "username": username,
                                "password": encrypted_pwd
                            }
                        )
                        return await f(request, *args, **kwargs)
                return json({"status": False, "message": "UnAuthorized User"}, 401)
            except Exception as exe:
                session.rollback()
                return json({"status": False, "message": "Invalid Authentication", "error": exe}, 403)
            finally:
                session.close()
        return wrapper
    return outer_wrapper

def check_url(json_format=False):
    def outer_wrapper(f):
        async def wrapper(request, *args, **kwargs):
            if json_format:
                url_identifier = request.json.get("identifier")
            else:
                url_identifier = request.form.get("identifier")
            if not url_identifier:
                return json({"status": False, "message": "URL Identifier is required"}, 403)
            session = get_session()
            try:
                urls = session.query(Url).filter(Url.identifier==url_identifier).all()
                if urls:
                    return json({"status": False, "message": "given URL with identifier {} already exists!".format(url_identifier)}, 403)
                return await f(request, *args, **kwargs)
            except Exception as exe:
                session.rollback()
                return json({"status": False, "message": "Invalid Authentication", "error": exe}, 403)
            finally:
                session.close()
        return wrapper
    return outer_wrapper

def check_existing_url(f):
    async def wrapper(request, *args, **kwargs):
        url_ids = request.args.get("url_id", None)
        session = get_session()
        try:
            url_objs = session.query(Url).filter(Url.id.in_(url_ids)).all()
            if not url_objs:
                return json({"success": "no url found"}, 404)
            return await f(request, *args, **kwargs)
        except Exception as exe:
            session.rollback()
            return json({"status": False, "error": exe}, 403)
        finally:
            session.close()
    return wrapper
