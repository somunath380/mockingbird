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

### Installation
#### Local Development
1. Install Docker on local machine
2. Clone the repository: `git clone https://github.com/somunath380/mockingbird`
3. Navigate to the project directory: `cd mockingbird`
4. use command `docker compose up` to create the application container

### API Documentation and Usage

| Column 1 Method | Column 2 Endpoint | Description |
| --- | --- | --- |
| GET | api/v1/url | Get a list of all urls |
| GET | api/v1/url{url_id} | Get information about a specific url |
| GET | api/v1/url{identifier} | Get information about a specific url |
| POST | api/v1/url | Add a new url |
| PUT | api/v1/url{url_id} | Update a specific url data (pending)|
| POST | api/v1/url/file | Upload file |
| PUT | api/v1/url/file{url_id} | Update file of a url |

### Authentication
