from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_FORM = '''
<form method="get" action="/add_form">
    <input type="number" name="a" placeholder="Число A" required>
    +
    <input type="number" name="b" placeholder="Число B" required>
    <button type="submit">Сложить</button>
</form>
'''

@app.route('/')
def index():
    return HTML_FORM

@app.route('/add_form', methods=['GET'])
def add_form():
    a = request.args.get('a', type=int)
    b = request.args.get('b', type=int)
    if a is None or b is None:
        return 'Ошибка: введите оба числа', 400
    return f'{a} + {b} = {a + b}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
