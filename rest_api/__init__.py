from quart import Quart, request
import quart
from quart_cors import cors
import time
import os
from .api import api

# Init app
app = Quart(__name__, static_folder=None)
app.url_map.strict_slashes = False
cors(app, allow_origin="*")


@app.get("/")
async def index():
    return await quart.send_file("build/index.html")

@app.get("/assets/<path:path>")
async def assets(path):
    return await quart.send_from_directory("build/", path)
app.register_blueprint(api)