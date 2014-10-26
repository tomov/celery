from app import app
from tasks import add_together

@app.route('/')
def index():
    return 'Hello'

@app.route('/add/<a>/<b>')
def add(a, b):
    result = add_together.delay(a, b)
    ans = result.wait()
    return str(ans)
