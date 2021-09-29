
import os
import time
import requests

from flask import Flask, jsonify

import logging
from jaeger_client import Config
from flask_opentracing import FlaskTracer

import redis
import redis_opentracing

app = Flask(__name__)

rdb = redis.Redis(host='redis-primary.default.svc.cluster.local', port=6379, db=0)

def initialize_tracer():
  config = Config(
      config={
          'sampler': {'type': 'const', 'param': 1}
      },
      service_name='hello-world')
  return config.initialize_tracer() # also sets opentracing.tracer



flask_tracer = FlaskTracer(initialize_tracer, True, app)


#starter code
#tracer = init_tracer('test-service')

# not entirely sure but I believe there's a flask_opentracing.init_tracing() missing here
redis_opentracing.init_tracing(flask_tracer, trace_all_classes=False)



@app.route('/')
def hello_world():
    return 'Hello World!'



@app.route('/alpha')
def alpha():
    parent_span = flask_tracer.get_span()
    github_url = "https://api.github.com/repos/opentracing/opentracing-python/pulls"
    with opentracing.start_span('github-api', child_of=parent_span) as span:
        span.set_tag("http.url",github_url)
        r = requests.get(github_url)
        span.set_tag("http.status_code", r.status_code)

    with opentracing.start_span('parse-json', child_of=parent_span) as span:
        json = r.json()
        span.set_tag("pull_requests", len(json))
        pull_request_titles = map(lambda item: item['title'], json)

    return 'PRs: ' + ', '.join(pull_request_titles)


 
@app.route('/beta')
def beta():
    r = requests.get("https://www.google.com/search?q=python")
    dict = {}
    for key, value in r.headers.items():
        print(key, ":", value)
        dict.update({key: value})
    return jsonify(dict)      



@app.route('/writeredis') # needed to rename this view to avoid function name collision with redis import
def writeredis():
    # start tracing the redis client
    redis_opentracing.trace_client(rdb)    
    r = requests.get("https://www.google.com/search?q=python")
    dict = {}
    # put the first 50 results into dict
    for key, value in r.headers.items()[:50]:
        print(key, ":", value)
        dict.update({key: value})
    rdb.mset(dict)    
    return jsonify(dict)      




if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))