from typing import Dict
import hashlib
import os
import aiofiles
from sanic.log import logger

async def create_basedir():
    current_dir = os.getcwd()
    logger.info(f"current directory {current_dir}")
    global_folder = os.path.abspath(os.path.join(current_dir, os.pardir))
    logger.info(f"global directory {global_folder}")
    global_folder_path = os.path.join(current_dir, 'files')
    logger.info("checking files folder")
    if not os.path.exists(global_folder_path):
        logger.info("created files folder")
        os.mkdir(global_folder_path)
    logger.info("files folder already exisis")
    basedir = global_folder_path
    return basedir

async def encrypt_pwd(user_details: Dict) -> str:
    username = user_details.get("username")
    password = user_details.get("password")
    userdetails: str = (username + password).encode("utf-8")
    secret = hashlib.sha256(userdetails).hexdigest()
    return secret

async def create_file_path(filename, foldername):
    basedir = await create_basedir()
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    upload_folder_path = os.path.join(basedir, foldername)
    if not os.path.exists(upload_folder_path):
        upload_folder_path = os.path.join(basedir, foldername)
        os.mkdir(upload_folder_path)
    filepath = os.path.join(upload_folder_path, filename)
    return filepath

async def write_to_file(filepath, file_obj):
    async with aiofiles.open(filepath, 'wb') as file:
        await file.write(file_obj.body)
    if not os.access(filepath, os.X_OK):
        current_permissions = os.stat(filepath).st_mode
        new_permissions = current_permissions | 0o100
        os.chmod(filepath, new_permissions)
