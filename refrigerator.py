from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return ''
    else:
        #return "This is a get request"
        return render_template('refrigerator2.html')

if __name__ == "__main__":
    app.run()
