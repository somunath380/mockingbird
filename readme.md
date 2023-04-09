objective:
    a service that can be used to send pre-defined data through http response or dynamic http response

process:
    a user will create a username and password
    using that username and password the server will give 1 token to the user
        1. Basic auth token
    the user will be authenticated with basic auth token

    then the user will store the files/scripts in mongodb and the location url will be stored in the postgres db

    to store user tokens a cache-layer will be needed. choice: redis # this is for future

    ** for now the files will be stored on server in a folder called files
    ** it is the sole responsibility of the user to delete the files that he/she has uploaded
    ** otherwise the files will be deleted after a certain amount of time

    the file that is being stored can be of 2 types
        1. it can be static file or non-executable file e.g PDF's/ TEXT files
        2. it can be executable python script files
    
    the response will be dependent of the type of file being stored for dynamic responses.
    ** the exec binary field is used for this segregation

    
************************* there is 2 type of API ******************************
1. The API to upload file (executable or normal file) with given url
when that url will be hit server will send response of file stream OR output of executable file

2. The normal API which will output the normal JSON formatted output when that url will be hit


database scheme
tables

User-
    id: Int primary key
    uid: Integer -> Url.user_id
    username: String
    Password: Stringified Hash value
    token: Stringified Hash value

** the token will be expired after a certain amount of time, on re-login new value will be SET

Url-
    id: Int primary key
    user_id: Integer --index_key, --foreign_key -> User.uid
    identifier: String -- index_key
    exc_path: String -- for storing python scripts/any file/ pdf absolute path index_key
    method: String
    body: Json
    response: Json
    latency: Int
    headers: Json
    status_code: Int
    exec: Binary

relationship-
    User.id == Url.user_id
    one to many relationship

data validation is done by marshmallow python package


************* Structure *******************

server.py --global-level.  will create the app object
api/base_handler.py will contain BaseHandler(HTTPHandler)
api/handlers.py contains all handlers
urls.py will contain all url endpoints


************* have to do ***************

change decorators: each handler should have its own middleware
add delete mechanism by which uploaded files will be deleted (manually or after certain amount of time)