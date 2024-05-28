import json
import logging
import datetime

from flask import Flask

app = Flask(__name__)

def log_msg(endpoint_name):
    time_stamp = datetime.datetime.now()
    app.logger.debug(f"{time_stamp}, { endpoint_name} endpoint was reached")

@app.route("/")
def hello():
    log_msg('hello')
    return "Hello World!"


@app.route("/status")
def status():
    log_msg('status')
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response


@app.route("/metrics")
def metrics():
    log_msg('metrics')
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"UserCount":140,"UserCountActive":23}}),
            status=200,
            mimetype='application/json'
    )

    return response

if __name__ == "__main__":
    
    logging.basicConfig(
        filename="app.log",
        level=logging.DEBUG
    )
    
    app.run(host='0.0.0.0')
 