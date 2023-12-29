from quart import Blueprint, Quart, request, current_app as app
import time
import os

import quart

from .home import home_bp
from .me import me_bp
from .inbox import inbox_bp
from .posts import posts_bp
from .users import users_bp
from .chats import chats_bp
from .search import search_bp
from .admin import admin_bp

api = Blueprint("api", __name__, url_prefix="/api/")



@api.before_request
async def check_repair_mode():
    if app.supporter.repair_mode and request.path != "/status":
        return {"error": True, "type": "repairModeEnabled"}, 503


@api.before_request
async def check_ip():
    request.ip = (request.headers.get("Cf-Connecting-Ip", request.remote_addr))
    if request.path != "/status" and app.supporter.blocked_ips.search_best(request.ip):
        return {"error": True, "type": "ipBlocked"}, 403


@api.before_request
async def check_auth():
    # Init request user and permissions
    request.user = None
    request.permissions = 0

    # Get token
    token = request.headers.get("token")

    # Authenticate request
    if token and request.path != "/status":
        account = app.files.db.usersv0.find_one({"tokens": token}, projection={
            "_id": 1,
            "permissions": 1,
            "ban.state": 1,
            "ban.expires": 1
        })
        if account:
            if account["ban"]["state"] == "perm_ban" or (account["ban"]["state"] == "temp_ban" and account["ban"]["expires"] > time.time()):
                return {"error": True, "type": "accountBanned"}, 403
            request.user = account["_id"]
            request.permissions = account["permissions"]


@api.get("/")  # Welcome message
async def index():
	return "Hello world! The Meower API is working, but it's under construction. Please come back later.", 200


@api.get("/ip")  # Deprecated
async def ip_tracer():
	return "", 410

@api.get("/v0/cloudlink")
async def cl():
    if request.host.split(":")[0] == "localhost":
        return quart.redirect("ws://localhost:3000")

    return  quart.redirect("wss://server.meower.org")

@api.get("/favicon.ico")  # Favicon, my ass. We need no favicon for an API.
async def favicon_my_ass():
	return "", 200


@api.get("/status")
async def get_status():
    return {
        "scratchDeprecated": True,
        "registrationEnabled": app.supporter.registration,
        "isRepairMode": app.supporter.repair_mode,
        "ipBlocked": (app.supporter.blocked_ips.search_best(request.ip) is not None),
        "ipRegistrationBlocked": (app.supporter.registration_blocked_ips.search_best(request.ip) is not None)
    }, 200


@api.get("/statistics")
async def get_statistics():
    return {
        "error": False,
        "users": app.files.db.usersv0.estimated_document_count(),
        "posts": app.files.db.posts.estimated_document_count(),
        "chats": app.files.db.chats.estimated_document_count()
    }, 200


@api.errorhandler(400)  # Bad request
async def bad_request(e):
	return {"error": True, "type": "badRequest"}, 400


@api.errorhandler(401)  # Unauthorized
async def unauthorized(e):
	return {"error": True, "type": "Unauthorized"}, 401


@api.errorhandler(403)  # Missing permissions
async def missing_permissions(e):
    return {"error": True, "type": "missingPermissions"}, 403


@api.errorhandler(404)  # We do need a 404 handler.
async def not_found(e):
	return {"error": True, "type": "notFound"}, 404


@api.errorhandler(405)  # Method not allowed
async def method_not_allowed(e):
	return {"error": True, "type": "methodNotAllowed"}, 405


@api.errorhandler(429)  # Too many requests
async def too_many_requests(e):
	return {"error": True, "type": "tooManyRequests"}, 429


@api.errorhandler(500)  # Internal
async def internal(e):
	return {"error": True, "type": "Internal"}, 500


@api.errorhandler(501)  # Not implemented
async def not_implemented(e):
      return {"error": True, "type": "notImplemented"}, 501


# Register blueprints
api.register_blueprint(home_bp)
api.register_blueprint(me_bp)
api.register_blueprint(inbox_bp)
api.register_blueprint(posts_bp)
api.register_blueprint(users_bp)
api.register_blueprint(chats_bp)
api.register_blueprint(search_bp)
api.register_blueprint(admin_bp)