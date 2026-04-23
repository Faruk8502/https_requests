from flask import Flask, request

app = Flask(__name__)

@app.route('/add', methods=['GET'])
def add():
    # Получаем параметры a и b из URL (например, /add?a=2&b=2)
    a = request.args.get('a', type=int)
    b = request.args.get('b', type=int)

    # Проверяем, что оба числа переданы
    if a is None or b is None:
        return 'Пожалуйста, укажите параметры a и b (целые числа)', 400

    result = a + b
    # Можно вернуть просто текст
    return str(result)

if __name__ == '__main__':
    # Запускаем сервер на localhost, порт 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
