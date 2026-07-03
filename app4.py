import os
import time
import threading
import queue
from flask import Flask, render_template, request, jsonify, Response, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Глобальные переменные для управления потоком
running = False
stop_flag = False
message_queue = queue.Queue()
worker_thread = None

def worker(content):
    """Функция, эмулирующая обработку .tn файла."""
    global running, stop_flag
    # Разбиваем содержимое на строки и отправляем по одной с задержкой
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if stop_flag:
            break
        message_queue.put(f"Строка {idx+1}: {line}")
        time.sleep(0.5)  # имитация работы
    if not stop_flag:
        message_queue.put("✅ Обработка завершена")
    running = False
    stop_flag = False

@app.route('/')
def index():
    return render_template('index_2.html')

@app.route('/editor')
def editor():
    return render_template('editor.html')


@app.route('/api/load', methods=['GET'])
def load_file():
    """Загружает содержимое .tn файла по имени (параметр ?filename="""
    filename = request.args.get('filename', 'default.tn')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'content': content, 'filename': filename})

@app.route('/api/save', methods=['POST'])
def save_file():
    """Сохраняет содержимое .tn файла (передаётся JSON с полями filen>"""
    data = request.get_json()
    if not data or 'filename' not in data or 'content' not in data:
        return jsonify({'error': 'Missing filename or content'}), 400
    filename = data['filename']
    # Чтобы избежать подмены пути, разрешаем только буквы, цифры, точ>
    if not filename.replace('.', '').replace('-', '').isalnum():
        return jsonify({'error': 'Invalid filename'}), 400
    if not filename.endswith('.tn'):
        filename += '.tn'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data['content'])
    return jsonify({'status': 'saved', 'filename': filename})

# ---------- API ----------
''''@app.route('/api/load', methods=['GET'])
def load_file():
    filename = request.args.get('filename', '')
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'content': content, 'filename': filename})
'''
@app.route('/api/run', methods=['POST'])
def run_process():
    global running, stop_flag, worker_thread, message_queue
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing content'}), 400
    if running:
        return jsonify({'error': 'Process already running'}), 409

    # Очищаем очередь перед новым запуском
    while not message_queue.empty():
        message_queue.get()
    stop_flag = False
    running = True
    worker_thread = threading.Thread(target=worker, args=(data['content'],))
    worker_thread.daemon = True
    worker_thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_process():
    global stop_flag, running
    if not running:
        return jsonify({'error': 'No process running'}), 400
    stop_flag = True
    # Ждём завершения потока (необязательно)
    return jsonify({'status': 'stopping'})

@app.route('/api/stream')
def stream():
    """SSE-поток для отправки сообщений из очереди."""
    def generate():
        global running
        while True:
            # Ждём сообщение из очереди (блокируемся, пока не появится)
            try:
                msg = message_queue.get(timeout=1)
            except queue.Empty:
                # Если поток завершён и очередь пуста, выходим
                if not running and message_queue.empty():
                    break
                continue
            yield f"data: {msg}\n\n"
            # Если процесс завершился и очередь пуста – завершаем SSE
            if not running and message_queue.empty():
                break
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'  # отключаем буферизацию nginx
    })

if __name__ == '__main__':
    # Запуск на всех интерфейсах (публичный IP)
    # Порт 5000 – стандартный для Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
