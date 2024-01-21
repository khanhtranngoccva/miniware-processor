from server.flask_server import app
from server import env
import server.error_handling
import server.controllers.executable
import server.controllers.analysis
import os

server.error_handling.add_error_handling(app)
server.controllers.executable.routes(app)
server.controllers.analysis.routes(app)

debug = bool(os.environ.get('DEBUG'))

if __name__ == '__main__':
    app.run("0.0.0.0", 4000, debug=debug)
