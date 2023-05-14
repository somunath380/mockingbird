#**Project: Mockingbird**
## Description
This project provides a mock server that allows for file streaming and dynamic responses, making it ideal for testing applications that require such functionality. With this server, developers can easily simulate different scenarios and test their applications' ability to handle various types of input and output.

## Features of this mock server include:
    * File streaming capabilities
    * Dynamic response generation
    * Support for various HTTP methods (GET, POST, PUT, DELETE)
    * Easy setup and configuration

To get started, simply follow the instructions in the Getting Started section below.

I hope that this project helps you to streamline your testing process and ensures that your applications work as expected.

### Installation and startup
1. Install Docker on local machine
2. Clone the repository: `git clone https://github.com/somunath380/mockingbird`
3. Navigate to the project directory: `cd mockingbird`
4. use command `chmod +x docker-run.sh` to set the executable flag on docker-run.sh file
5. now run `./docker-run.sh start` command.
6. it will prompt you to put any value which will be used to generate an API TOKEN that will be used later for authentication
7. the above command will create docker image of mockingbird and pull up postgres image from docker registory
8. thats all you need to get your server up and running

### Putting your server on public using ngrok
1. install ngrok agent from https://ngrok.com/docs/getting-started/
2. verify that it is installed by running `ngrok -h`
3. sign-up freely to ngrok dashboard https://dashboard.ngrok.com/get-started/setup
4. go to Your-Authtoken page to get your auth token
5. and start ngrok on your bash `ngrok http 8888`
6. it will prompt a Forwarding URL, copy that
7. now use that forwarding url as domain and the API endpoints described below to use the service from ANYWHERE

Holaa!!!

### API Documentation and Usage

| Column 1 Method | Column 2 Endpoint | Description |
| --- | --- | --- |
| GET | api/v1/url | Get a list of all urls |
| GET | api/v1/url{url_id} | Get information about a specific url |
| GET | api/v1/url{identifier} | Get information about a specific url |
| POST | api/v1/url | Add a new url |
| PUT | api/v1/url{url_id} | Update a specific url data|
| POST | api/v1/url/file | Upload file |
| PUT | api/v1/url/file{url_id} | Update file of a url |
| DELETE | api/v1/url/delete | Delete a file contained url |

use [method] /mockingbird/<created url> to get the saved response.

