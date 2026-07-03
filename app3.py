import os
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------- СТРАНИЦЫ ----------
@app.route('/')
def index():
    """Приветственная страница."""
    return render_template('index.html')

@app.route('/editor')
def editor():
    """Страница редактора."""
    return render_template('editor_2.html')

# ---------- API ДЛЯ РАБОТЫ С ФАЙЛАМИ .tn ----------
@app.route('/api/load', methods=['GET'])
def load_file():
    """Загружает содержимое .tn файла по имени (параметр ?filename=...)."""
    filename = request.args.get('filename', 'default.tn')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'content': content, 'filename': filename})

@app.route('/api/save', methods=['POST'])
def save_file():
    """Сохраняет содержимое .tn файла (передаётся JSON с полями filename и content)."""
    data = request.get_json()
    if not data or 'filename' not in data or 'content' not in data:
        return jsonify({'error': 'Missing filename or content'}), 400
    filename = data['filename']
    # Чтобы избежать подмены пути, разрешаем только буквы, цифры, точки, дефисы
    if not filename.replace('.', '').replace('-', '').isalnum():
        return jsonify({'error': 'Invalid filename'}), 400
    if not filename.endswith('.tn'):
        filename += '.tn'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data['content'])
    return jsonify({'status': 'saved', 'filename': filename})

# Для удобства – список сохранённых файлов
@app.route('/api/list', methods=['GET'])
def list_files():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.tn')]
    return jsonify(files)

if __name__ == '__main__':
    # Запуск на всех интерфейсах (публичный IP)
    # Порт 5000 – стандартный для Flask
    app.run(host='0.0.0.0', port=5000, debug=True)