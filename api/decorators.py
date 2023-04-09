from validations.validate import UserSchema
from typing import Dict, Text
from db.models import User, Url
from sanic.response import json
import base64
from api.helper import encrypt_pwd
from db.connection import get_session
from functools import wraps


def is_authorized(func):
    """Middleware to check if the request is authorized for processing."""
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        session = get_session()
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header is None:
                return json({"status": False, "message": "unable to Authorize"}, 400)
            auth_decoded = base64.b64decode(auth_header[6:]).decode()
            username, password = auth_decoded.split(":")
            user_obj = session.query(User).filter(User.username == username).first()
            if not user_obj:
                return json({"success": False, "message": "no user found"}, status=404)
            else:
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
                    return await func(self, request, *args, **kwargs)
            return json({"status": False, "message": "UnAuthorized User"}, 401)
        except Exception as exe:
            session.rollback()
            return json({"status": False, "message": "Invalid Authentication", "error": exe}, 403)
        finally:
            session.close()
    return wrapper



def check_existing_user(func):
    """Middleware to check if user already exists or not."""
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        session = get_session()
        try:
            request_data: Dict = request.json
            request_data = UserSchema().load(request_data)
            username: Text = request_data.get("username")
            user_obj = session.query(User).filter(User.username == username).first()
            if user_obj:
                return json({"status": False, "message": "user with username {} already exists".format(username)})
            return await func(self, request, *args, **kwargs)
        except Exception:
            session.rollback()
        finally:
            session.close()
    return wrapper



def check_existing_url(json_format=False):
    """Middleware to check if the url already exists or not.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, request, *args, **kwargs):
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
                return await func(self, request, *args, **kwargs)
            except Exception as exe:
                session.rollback()
                return json({"status": False, "message": "Invalid Authentication", "error": exe}, 403)
            finally:
                session.close()
        return wrapper
    return decorator


def is_admin(func):
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        session = get_session()
        try:
            user_id = kwargs["id"]
            print(user_id)
            admin = session.query(User).filter(User.id == 1).first()
            if admin.id != user_id:
                return json({"success": False, "message": "user is not admin"}, 400)
            return await func(self, request, *args, **kwargs) 
        except Exception as ex:
            session.rollback()
        finally:
            session.close()
    return wrapper
