from src import app, socket

if __name__ == '__main__':
    socket.run(app=app, host="0.0.0.0" debug=True, port=8000, allow_unsafe_werkzeug=True)
