from sanic import Sanic
from sanic.response import json
from db.setup_db import check_or_create_tables, close_all_db_sessions
from urls import blueprint_v1
from sanic.log import logger

app = Sanic(__name__)
app.blueprint(blueprint_v1)

@app.listener("before_server_start")
async def connect_to_db(app):
    """Connects to the database.
    
    Args:
        app (object): the sanic application object.

    Returns:
        None."""
    await check_or_create_tables()

@app.listener("before_server_stop")
async def close_db_connection(app):
    """Closes db connections before stopping the server.
    
    Args:
        app (object): sanic application object. 
        
    Returns:
        None."""
    await close_all_db_sessions()

@app.route('/', methods=['GET'])
async def ping(request):
    return json({'response': 'pong!'}, 200)


# @app.route("/mockingbird/<path:path>", methods=['GET', 'POST', 'PUT'])
# async def catch_all(request, path):
#     return json({"url_path": path, "method": request.method}, 200)






# UPDATE
# @app.route('/file/change', methods=['POST', 'PUT'])
# async def change_file_contents(request):
#     path = request.form.get('path')
#     file_obj = request.files.get('file')
#     if not os.path.exists(path):
#         return json({'msg': 'no path exists'}, 404)
#     await write_to_file(file_obj.body, path, command="ab")
#     return json({'msg':'file data modified'}, 200)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, auto_reload=True, debug=True, workers=1)


