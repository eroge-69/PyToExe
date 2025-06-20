import subprocess
import os
import time

# === Your project paths ===
backend_dir   = r"D:\Prajwal\Bryckel.ai\Code\Bryckel-backend"
frontend_dir  = r"D:\Prajwal\Bryckel.ai\Code\Bryckel-frontend"
docker_image  = "qdrant/qdrant"
rabbitmq_sbin = r"C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.7\sbin"  # adjust version

def open_terminal(cmd: str):
    """
    Opens a fresh Windows terminal window and runs the given command string.
    The window stays open after the command completes so you can see logs.
    """
    subprocess.Popen(
        f'start cmd /K "{cmd}"',
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

def start_frontend():
    # 1. Frontend: cd into folder, npm run dev
    cmd = f'cd /d "{frontend_dir}" && npm run dev'
    open_terminal(cmd)

def start_backend():
    # 2. Backend:
    #    activate venv, cd to bryckel subfolder, then run Django dev server
    activate = os.path.join(backend_dir, "env", "Scripts", "activate")
    # assume manage.py lives inside a "bryckel" subfolder of backend_dir
    manage_dir = os.path.join(backend_dir, "bryckel")
    cmd = (
        f'cd /d "{backend_dir}" && '
        f'call "{activate}" && '
        f'cd /d "{manage_dir}" && '
        f'python manage.py runserver'
    )
    open_terminal(cmd)

def start_celery():
    # 3. Celery:
    #    activate venv, cd to bryckel, then launch worker with your flags
    activate = os.path.join(backend_dir, "env", "Scripts", "activate")
    celery_cmd = (
        f'celery -A bryckel worker -l info '
        f'--concurrency=1 --without-gossip --pool=gevent'
    )
    cmd = (
        f'cd /d "{backend_dir}" && '
        f'call "{activate}" && '
        f'cd /d "{os.path.join(backend_dir, "bryckel")}" && '
        f'{celery_cmd}'
    )
    open_terminal(cmd)

def start_docker():
    # 4. Docker:
    #    run your qdrant image, mapping port 6333
    # run detached and close terminal after
    cmd = f'docker run --rm -p 6333:6333 -d {docker_image}'
    subprocess.run(cmd, shell=True)

def start_rabbitmq():
    # 5. RabbitMQ:
    #    start RabbitMQ server using rabbitmq-server.bat
    rabbitmq_server_bat = os.path.join(rabbitmq_sbin, "rabbitmq-server.bat")
    if os.path.exists(rabbitmq_server_bat):
        open_terminal(f'cd /d "{rabbitmq_sbin}" && call "{rabbitmq_server_bat}"')
    else:
        print(f"RabbitMQ server not found at {rabbitmq_server_bat}. Please check your installation.")

if __name__ == "__main__":
    start_rabbitmq()
    start_frontend()
    start_backend()
    start_celery()
    start_docker()
