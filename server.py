from sanic import Sanic
from sanic.response import json
from sanic import response
import os
import aiofiles
import multiprocessing
from db.setup_db import check_or_create_tables, close_all_db_sessions
from sanic.log import logger
from urls import blueprint_v1

app = Sanic(__name__)
app.blueprint(blueprint_v1)

@app.listener("before_server_start")
async def connect_to_db(app):
    await check_or_create_tables()

@app.listener("before_server_stop")
async def close_db_connection(app):
    await close_all_db_sessions()

@app.route('/', methods=['GET'])
async def ping(request):
    return json({'response': 'pong!'}, 200)


# @app.route("/mockingbird/<path:path>", methods=['GET', 'POST', 'PUT'])
# async def catch_all(request, path):
#     return json({"url_path": path, "method": request.method}, 200)



# async def write_to_file(data, filepath, command):
#     async with aiofiles.open(filepath, command) as file:
#         await file.write(data)
#     return




# READ
# @app.route('/file/download', methods=['POST'])
# async def download(request):
#     path = request.json.get('path')
#     if not os.path.exists(path):
#         return json({'msg': 'no path exists'}, 404)
#     return await response.file_stream(
#         path,
#         chunk_size=1024,
#         mime_type="application/metalink4+xml",
#         headers={
#             "Content-Disposition": 'Attachment; filename="nicer_name.meta4"',
#             "Content-Type": "application/metalink4+xml",
#         }
#     )


# UPDATE
# @app.route('/file/change', methods=['POST', 'PUT'])
# async def change_file_contents(request):
#     path = request.form.get('path')
#     file_obj = request.files.get('file')
#     if not os.path.exists(path):
#         return json({'msg': 'no path exists'}, 404)
#     await write_to_file(file_obj.body, path, command="ab")
#     return json({'msg':'file data modified'}, 200)


# DELETE
# @app.route('/file/delete', methods=['GET'])
# async def delete_folder(request):
#     os.system(f'rm -rf {basedir}')
#     return json({'status': 'SUCCESS', 'msg': 'all folders deleted!'}, 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, auto_reload=True, debug=True, workers=1)


