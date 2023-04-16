from typing import Dict, Text
import os
import aiofiles
from sanic.log import logger
import subprocess
from common.constants import MAX_EXECUTION_TIME

async def create_basedir():
    """Creates the base directory where the files will be stored.
    Args: 
        None.
    Returns:
        basedir (str): location path."""
    current_dir: Text = os.getcwd()
    logger.info(f"create_basedir, current directory {current_dir}")
    global_folder: Text = os.path.abspath(os.path.join(current_dir, os.pardir))
    logger.info(f"create_basedir, global directory {global_folder}")
    global_folder_path: Text = os.path.join(current_dir, 'files')
    logger.info("create_basedir, checking files folder")
    if not os.path.exists(global_folder_path):
        logger.info("create_basedir, created files folder")
        os.mkdir(global_folder_path)
    logger.info("create_basedir, files folder already exisis")
    basedir: Text = global_folder_path
    return basedir


async def create_file_path(filename, foldername):
    """Creates the location path where the file will be saved in the server.
    Args:
        filename (str): name of the file.
        foldername (str): name of the folder.
    Returns:
        filepath (str): location path."""

    basedir: Text = await create_basedir()
    logger.info(f"create_file_path, basedir: {basedir}")
    if not os.path.exists(basedir):
        logger.info(f"create_file_path, creating basedir: {basedir}")
        os.mkdir(basedir)
    upload_folder_path: Text = os.path.join(basedir, foldername)
    logger.info(f"upload_folder_path, {upload_folder_path}")
    if not os.path.exists(upload_folder_path):
        logger.info(f"upload_folder_path, creating...")
        upload_folder_path: Text = os.path.join(basedir, foldername)
        os.mkdir(upload_folder_path)
    filepath: Text = os.path.join(upload_folder_path, filename)
    logger.info(f"create_file_path, filepath: {filepath}")
    return filepath


async def write_to_file(filepath, file_obj):
    """Writes the file contents to the specified filepath.
    Args:
        filepath (str): filepath.
        file_obj (object): file object from request.file object"""
    async with aiofiles.open(filepath, 'wb') as file:
        await file.write(file_obj.body)
    if not os.access(filepath, os.X_OK):
        current_permissions: int = os.stat(filepath).st_mode
        new_permissions: int = current_permissions | 0o100
        os.chmod(filepath, new_permissions)


async def execute_file(filepath):
    try:
        logger.info("execute_file, executing the file {}".format(filepath))
        result = subprocess.run(["python", filepath], check=True, timeout=MAX_EXECUTION_TIME, capture_output=True).stdout.decode("utf-8")
        logger.info("execute_file, file execution complete")
        return eval(result)
    except FileNotFoundError as exe:
        logger.exception(f"execute_file, FileNotFoundError: {exe}")
        return {}
    except subprocess.CalledProcessError as exe:
        logger.exception(f"execute_file, return_code: {exe.returncode}, CalledProcessError: {exe}")
        return {}
    except subprocess.TimeoutExpired as exe:
        logger.exception(f"execute_file, TimeoutExpired: {exe}")
        return {}

