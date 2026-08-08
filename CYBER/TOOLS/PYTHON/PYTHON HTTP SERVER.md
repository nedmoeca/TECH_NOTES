
Python comes with a **built-in HTTP server module** called `http.server` (Python 3) or `SimpleHTTPServer` (Python 2). It's mainly used for:

- Serving static files (like HTML, CSS, JS, images).
- Quickly testing front-end code.
- Running lightweight development servers.


## How to Start a Simple Server

### Python 3

```bash
python -m http.server
```

- Serves files from the current directory on port `8000`.
- Access it in your browser at: `http://localhost:8000`

### Python 2

```bash
python -m SimpleHTTPServer 8000
```

### Custom Port and Directory

```bash
python -m http.server 8080 --directory my_folder/
```

- Serves `my_folder/` at `http://localhost:8080`

### Key Classes and Methods

|Component|Description|
|---|---|
|`HTTPServer`|Main server object (host, port, handler)|
|`BaseHTTPRequestHandler`|Customize HTTP methods like `do_GET`, `do_POST`|
|`self.send_response(code)`|Send status code like `200`, `404`|
|`self.send_header()`|Add headers|
|`self.end_headers()`|Ends header section|
|`self.wfile.write()`|Write response body|

### Stopping the Server

To stop the server, press `Ctrl + C` in the terminal.

### Security Warning

The built-in server is **not secure** and should **not be used in production**. It's only for testing/development.


---

## Serving Files From Your Host - WEB

 This module turns your computer into a quick and easy web server that you can use to serve your own files, where they can then be downloaded by another computing using commands such as `curl` and `wget`.

Python3's "HTTPServer" will serve the files in the directory where you run the command, but this can be changed by providing options that can be found within the manual pages. Simply, all we need to do is run `python3 -m  http.server` in the terminal to start the module! In the snippet below, we are serving from a directory called "webserver", which has a single named "file".

```shell-session
tryhackme@linux3:/webserver# python3 -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Now, let's use `wget` to download the file using the 10.10.180.14 address and the name of the file. Remember, because the python3 server is running port 8000, you will need to specify this within your wget command. For example:

An example wget command of a web server running on port 8000

```shell-session
tryhackme@mymachine:~# wget http://10.10.180.14:8000/myfile
```

Note, you will need to open a new terminal to use `wget` and leave the one that you have started the Python3 web server in. This is because, once you start the Python3 web server, it will run in that terminal until you cancel it.

Let's take a look in the snippet below as an example:

```shell-session
tryhackme@linux3:/tmp# wget http://10.10.180.14:8000/file

2021-05-04 14:26:16  http://127.0.0.1:8000/file
Connecting to http://127.0.0.1:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: 51095 (50K) [text]
Saving to: ‘file’

file                    100%[=================================================>]  49.90K  --.-KB/s    in 0.04s

2021-05-04 14:26:16 (1.31 MB/s) - ‘file’ saved [51095/51095]
```

**Remember**, you will need to run the wget command in another terminal (while keeping the terminal that is running the Python3 server active). One flaw with this module is that you have no way of indexing, so you must know the exact name and location of the file that you wish to use.


---

## References