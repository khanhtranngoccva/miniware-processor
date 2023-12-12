from server.flask_server import app
import server.error_handling
import server.controllers.executable

server.error_handling.add_error_handling(app)
server.controllers.executable.routes(app)

if __name__ == '__main__':
    app.run("0.0.0.0", 4000)
