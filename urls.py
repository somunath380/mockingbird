from sanic.blueprints import Blueprint
from api.handlers import UserView, RegisterUser, UploadFileHandler, AddUrlHandler, GetUrlHandler, handle_request
blueprint_v1 = Blueprint("v1", url_prefix="/api/v1")

blueprint_v1.add_route(UserView.as_view(), '/user', methods=["GET", "DELETE"], name="get_or_delete_user")
blueprint_v1.add_route(RegisterUser.as_view(), '/user/register', methods=["POST"], name="add_user")
blueprint_v1.add_route(UploadFileHandler.as_view(), '/file/upload', methods=["POST"], name="upload_file")
blueprint_v1.add_route(AddUrlHandler.as_view(), '/create/url', methods=["POST"], name="create_url")
blueprint_v1.add_route(GetUrlHandler.as_view(), '/url', methods=["GET", "DELETE"], name="get_urls")

blueprint_v1.add_route(handle_request, '/mockingbird/<path:path>', methods=['GET', 'POST', 'PUT'])