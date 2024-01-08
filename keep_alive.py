from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
  return "RFBOT COMMANDS IS WORKING"

if __name__=="__main__":
  os.system("python main.py &")
  app.run(host="0.0.0.0", port=80)
