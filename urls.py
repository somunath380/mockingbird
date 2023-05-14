from sanic.blueprints import Blueprint
from api.handlers import UploadFileHandler, UrlHandler, handle_request, DeleteUrlHandler
blueprint_v1 = Blueprint("v1", url_prefix="/api/v1")
blueprint_v2 = Blueprint("v2", url_prefix="/mockingbird")

blueprint_v1.add_route(UploadFileHandler.as_view(), '/url/file', methods=["POST"], name="upload_file")
blueprint_v1.add_route(UrlHandler.as_view(), '/url', methods=["POST", "GET", "PUT"], name="get_post_urls")
blueprint_v1.add_route(DeleteUrlHandler.as_view(), '/url/delete', methods=["DELETE"], name="delete_url")

blueprint_v2.add_route(handle_request, '/<path:path>', methods=['GET', 'POST', 'PUT'])