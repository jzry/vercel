# Environment Variable Reference

A comprehensive list of all environment variables that are used by this program.
Not all of these are required to be set. Those that must be set will be labeled :exclamation:***Required***.

## File: `/process.env`

### PORT

:exclamation:***Required***

The port number that the Express server will communicate on.
Ports `80`, `8008`, and `8080` are typically used for HTTP. Port `443` is used for HTTPS.
For testing on localhost, you can use any port not being used by your computer.
For a list of commonly used ports see
[this wikipedia page](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers).

### MODE

:exclamation:***Required***

This can be either `development` or `production`.
If `development` is specified, then CORS security will be **disabled** and the React frontend will
**not** be served statically from Express.
If `production` is specified, then CORS security will be enabled and the React frontend will be
served statically from Express (Remember to run the frontend build script first!).

### PYTHON_CMD

Sets the string used to run Python. Depending on your system and configuration this could be
`python3`, `python`, or `py`. By default, `python3` is used.

### PROTOCOL

This can be either `http` or `https`. The default choice is `http`. If `https` is specified,
a second Express server will be created using HTTP on port 80 that redirects traffic to the HTTPS
server.

### KEY_FILE

:exclamation:***Required if PROTOCOL is set to `https`***

The path to a file containing an RSA key.

### CERT_FILE

:exclamation:***Required if PROTOCOL is set to `https`***

The path to a file containing an SSL certificate.

### TORCHSERVE

To use TorchServe, set this to `torchserve`. TorchServe is not used by default.

## File: `/frontend/.env`

> [!IMPORTANT]
> These variables should be up to date before performing a static build.
> If any changes are made to this file after a build, you must rebuild the frontend to use the
> latest values.

### REACT_APP_API_URL

:exclamation:***Required***

The base url for calling api endpoints. For example, `http://localhost:8080` would be
the correct url if the express server is running on port 8080 of your computer. If you would
like to test the website on devices on your local network, replace localhost with the ip address
of your computer.

