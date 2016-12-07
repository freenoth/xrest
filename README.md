# XREST API

It is a test-task for 'python backend-dev' vacancy.

A work example and docs here on [PythonAnywhere](http://freenoth.pythonanywhere.com/api/).
For testing use URL **`http://freenoth.pythonanywhere.com`** + **`endpoint`**

Based on:

+ Python 3.5.2
+ Django 1.9.3
+ Django REST Framework 3.5.3

Last test check:

    $ python3.5 manage.py test api
    Creating test database for alias 'default'...
    ................
    ----------------------------------------------------------------------
    Ran 16 tests in 0.760s
    OK
    Destroying test database for alias 'default'...

## Overview

An API provides a simple methods to work with filesystem on web-server. It has a flat structure (without folders). You can upload a file into web-server, download, update or delete it, also you can view a file metadata and a full list of stored files.

### UTF-8 encoding

All the strings passed from API have UTF-8 encoding.

### Datetime format

Dates used in API represents as strings and have the following format:

    '31.12.2016 23:59:59 +0000'

It use **`strftime`** format:

    '%d.%m.%Y %H:%M:%S %z'

### Response types

An API that provides to get file content have a binary data response. All other API and error handling have JSON-format responses. Every JSON have the same structure like:

    {
        "status": "OK",
        "code": 0,
        "data": ...
    }

**`Status`** can be **`'OK'`** or **`'Error'`** depending on API execution. **`'OK'`** means that API objective has benn succesfully completed.
**`Code`** implements an http status-code of response.
**`Data`** contains an useful information, such as an error description if error uccurs, or information about files.

There is a correct response example:

    $ curl -H 'Accept: application/json; indent=4' http:// <some URL> /api/files/10/meta/

    {
        "status": "OK",
        "code": 200,
        "data": {
            "name": "example.txt",
            "size": 454,
            "mime_type": "text/plain",
            "ext": ".txt",
            "created": "01.01.2016 00:44:52 +0000",
            "modified": "20.10.2016 13:58:01 +0000"
        }
    }

### API errors

When errors occurs the response will have a **`status`** = **`'Error'`**. Some additional information can be placed in **`'data'`** field. For example:

    $ curl -H 'Accept: application/json; indent=4' -X POST http:// <some URL> /api/files/

    {
        "status": "Error",
        "code": 400,
        "data": {
            "file": [
                "No file was submitted."
            ]
        }
    }

Every endpoint will return an **`405 Method not allowed`** if wrong method used.
An every error response have a right **`code`** value, that can help to identificate an error. For more information about specific status-codes read API description.

## Endpoints

API have the following implementation:

|   Method   |             Endpoint           |        Information       |
|:----------:| ------------------------------ | ------------------------ |
|   **GET**  | `/api/files/`                  | Get the list of files    |
|  **POST**  | `/api/files/`                  | Create new file          |
|   **GET**  | `/api/files/ <file-id> /`      | Get the file content     |
|   **PUT**  | `/api/files/ <file-id> /`      | Update file content      |
| **DELETE** | `/api/files/ <file-id> /`      | Delete file              |
|   **GET**  | `/api/files/ <file-id> /meta/` | Get the metadata of file |

* * *
## &#x27A5; **GET** `/api/files/`

This endpoint provide a method to get a full list of files stored on server.

#### PARAMETERS

No parameters.

#### RETURNS

The response **`data`** field contains a list of files, each file represented as a dictionary with **`id`** and **`name`** keys. If there is no files on server an empty-list will be returned.

+ **`id`** - can be used in other APIs as `file-id` parameter to define with which file to work.
+ **`name`** - name of file.

#### ERRORS

There is no registered error handlings for this endpoint.

#### EXAMPLES

Let\`s get a list of files:

    $ curl -H 'Accept: application/json; indent=4' http://freenoth.pythonanywhere.com/api/files/

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "status": "OK",
        "code": 200,
        "data": [
            {
                "id": 1,
                "name": "test.txt"
            },
            {
                "id": 2,
                "name": "example.txt"
            }
        ]
    }

Or using python **`requests`** lib:

    >>> import requests
    >>> url = 'http://freenoth.pythonanywhere.com/api/files/'
    >>> res = requests.get(url)
    >>> res.status_code
    200
    >>> res.content
    b'{"status":"OK","code":200,"data":[{"id":1,"name":"test.txt"},{"id":2,"name":"example.txt"}]}'

## &#x27A5; **POST** `/api/files/`

This endpoint provide a method to upload a file into the server.

#### PARAMETERS

**`file`** - a file type parameter that spicified a file to upload.

#### RETURNS

It returns a JSON-response with information about operation success or errors. In case of success **`data`** field will contain a dictionary with **`id`** and **`name`** that represent new file (structure like in list of files API) and **`code`** will be a **`201 Created`**.

#### ERRORS

A some errors can occurs during execution:

+ **`409 Conflict`** - if uploaded file already exists on server (means that file name **is busy**, not file identity).

+ **`400 Bad request`** - if there is an errors during file validation or no file was submited.

#### EXAMPLES

If html-form is used, it should have a **`enctype`** with value **`multipart/form-data`**, like this:

    <form method="post" action="/api/files/" enctype="multipart/form-data">
        <input name="file" value="" type="file">
        <input value="POST" type="submit">
    </form>

Let\`s try curl:

    $ curl -H 'Accept: application/json; indent=4' -i -X POST \
        -F file=@README.txt  http://freenoth.pythonanywhere.com/api/files/

    HTTP/1.1 201 Created
    Content-Type: application/json

    {
        "status": "OK",
        "code": 201,
        "data": {
            "id": 10,
            "name": "README.txt"
        }
    }

Or python **`requests`** lib:

    >>> import requests
    >>> url = 'http://freenoth.pythonanywhere.com/api/files/'
    >>> files = {'file': open('test.doc', 'rb')}
    >>> res = requests.post(url, files=files)
    >>> res.status_code
    201
    >>> res.content
    b'{"status":"OK","code":201,"data":{"id":12,"name":"test.doc"}}'

## &#x27A5; **GET** `/api/files/ <file-id> /`

This endpoint provide a method to download a file from the server.

#### PARAMETERS

**`file-id`** - an integer id that specified a file to download.

#### RETURNS

It returns a binary content of the specified file in case of success or a JSON-responce in case of error.

#### ERRORS

A some errors can occurs during execution:

+ **`404 Not found`** - if passed **`id`** and associated file does not exists.

#### EXAMPLES

Let\`s get some file from server:

    $ curl -i http://freenoth.pythonanywhere.com/api/files/8/

    HTTP/1.1 200 OK
    Content-Type: ('application/msword', None)
    Content-Length: 67469
    Content-Disposition: attachment; filename=test.doc

    Content: binary-data

Or python **`requests`** lib:

    >>> import requests
    >>> url = 'http://freenoth.pythonanywhere.com/api/files/8/'
    >>> res = requests.get(url)
    >>> res.status_code
    200
    >>> res.headers['Content-Length']
    '67469'
    >>> res.content
    b'...'

## &#x27A5; **PUT** `/api/files/ <file-id> /`

This endpoint provide a method to update file content on the server from content of uploaded file.

#### PARAMETERS

**`file-id`** - an integer id that specified a file to download.

**`file`** - a file type parameter that spicified a file to upload.

*Note: the name of uploaded file will be ignored, file used to update a content of the file that associated with* ***`file-id`***.

#### RETURNS

It returns a JSON-response with information about operation success or errors. In case of success **`data`** field will contain a dictionary with **`id`** and **`name`** that represent specified file (structure like in list of files API) and **`code`** will be a **`200 Ok`**.

#### ERRORS

A some errors can occurs during execution:

+ **`404 Not found`** - if passed **`id`** and associated file does not exists.

+ **`400 Bad request`** - if there is an errors during file validation or no file was submited.

#### EXAMPLES

Let\`s update some file on server:

    $ curl -H 'Accept: application/json; indent=4' -i -X PUT \
        -F file=@README.txt  http://freenoth.pythonanywhere.com/api/files/9/

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "status": "OK",
        "code": 200,
        "data": {
            "id": 9,
            "name": "test.txt"
        }
    }

Or python **`requests`** lib:

    >>> import requests
    >>> url = 'http://freenoth.pythonanywhere.com/api/files/9/'
    >>> files = {'file': open('test.doc', 'rb')}
    >>> res = requests.put(url, files=files)
    >>> res.status_code
    200
    >>> res.content
    b'{"status":"OK","code":200,"data":{"id":9,"name":"test.txt"}}'

## &#x27A5; **DELETE** `/api/files/ <file-id> /`

This endpoint provide a method to delete a file on the server.

#### PARAMETERS

**`file-id`** - an integer id that specified a file to delete.

#### RETURNS

It returns a JSON-response with result of deleting or error information. See more in examples.

#### ERRORS

A some errors can occurs during execution:

+ **`404 Not found`** - if passed **`id`** and associated file does not exists.

#### EXAMPLES

Trying to delete file:

    $ curl -H 'Accept: application/json; indent=4' -i -X DELETE \
        http://freenoth.pythonanywhere.com/api/files/2/

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "status": "OK",
        "code": 200,
        "data": {
            "result": [
                "File deleted"
            ]
        }
    }

Or python **`requests`** lib:

    >>> import requests
    >>> url = 'http://freenoth.pythonanywhere.com/api/files/8/'
    >>> res = requests.delete(url)
    >>> res.status_code
    200
    >>> res.content
    b'{"status":"OK","code":200,"data":{"result":["File deleted"]}}'

## &#x27A5; **GET** `/api/files/ <file-id> /meta/`

This endpoint provide a method to get some metadata of the file on the server.

#### PARAMETERS

**`file-id`** - an integer id that specified a file to get metadata.

#### RETURNS

It return a JSON-response that represent a metadata of the specified file or an error if occurs. A response **`data`** field contain a dictionary that represent file metadata, that contain information about filename, filesize in bytes, type of the content ([Media type](https://en.wikipedia.org/wiki/Media_type)), file extension, and information about date of file creation and last modifed.

#### ERRORS

A some errors can occurs during execution:

+ **`404 Not found`** - if passed **`id`** and associated file does not exists.

#### EXAMPLES

Let\`s get some meta:

    $ curl -H 'Accept: application/json; indent=4' -i  http://freenoth.pythonanywhere.com/api/files/10/meta/

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "status": "OK",
        "code": 200,
        "data": {
            "name": "README.txt",
            "size": 235,
            "mime_type": "text/plain",
            "ext": ".txt",
            "created": "01.11.2016 12:41:36 +0000",
            "modified": "06.12.2016 17:01:54 +0000"
        }
    }

Or python **`requests`** lib:

    >>> import requests
    >>> url = 'http://freenoth.pythonanywhere.com/api/files/10/meta/'
    >>> res = requests.get(url)
    >>> res.status_code
    200
    >>> res.content
    b'{"status":"OK","code":200,"data":{"name":"README.txt","size":235,"mime_type":"text/plain","ext":".txt","created":"06.12.2016 03:41:36 +0000","modified":"06.12.2016 03:41:36 +0000"}}'
