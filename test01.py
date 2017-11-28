from flask import Flask

app = Flask(__name__)

@app.route('/')
def helloworld():
    return 'hello world!'

@app.route('/mypage')
def mypagepage():
    return 'nice to meet you!'

# print('--- This is test line ---')
