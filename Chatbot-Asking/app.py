# import files
import os
import signal
import os
import platform
import socket
import subprocess
from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

app = Flask(__name__)

chatbot = ChatBot('ChatBot')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(chatbot.get_response(userText))


def find_available_port(start_port, end_port):
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result != 0:
            return port
    return None

def clear_previous_port(port):
    # Identify the process using the port
    if platform.system() == 'Windows':
        command = f"netstat -ano | findstr :{port}"
    else:
        command = f"lsof -i :{port}"

    process_info = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(process_info.stdout)

    # Terminate the process
    for line in process_info.stdout.splitlines():
        if 'LISTEN' in line:
            pid = line.split()[-1]
            if platform.system() == 'Windows':
                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
            else:
                subprocess.run(f"kill -9 {pid}", shell=True)

    # Use a different port
    new_port = find_available_port(port + 1, port + 10)
    return new_port

# Route to clear the previous port and get a new port
@app.route('/clear_port', methods=['GET'])
def clear_port():
    target_port = 5000  # Adjust to your desired port
    new_port = clear_previous_port(target_port)
    return {'new_port': new_port}

# Route to gracefully shut down the Flask server
@app.route('/shutdown', methods=['POST'])
def shutdown(os=None):
    print("Shutting down gracefully...")
    os.kill(os.getpid(), signal.SIGINT)
    return 'Server shutting down...'

# Modify the app.run() part to dynamically find an available port
if __name__ == "__main__":
    while True:
        new_port = find_available_port(5000, 5010)
        if new_port:
            app.run(port=new_port, debug=True)
            break
        else:
            print("Error: No available port found. Restarting...")