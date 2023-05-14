from sanic import Sanic
from sanic.response import json
from db.setup_db import check_or_create_tables, close_all_db_sessions
from urls import blueprint_v1, blueprint_v2
from sanic.log import logger


app = Sanic(__name__)
app.blueprint(blueprint_v1)
app.blueprint(blueprint_v2)

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, auto_reload=True, debug=True, workers=1)


