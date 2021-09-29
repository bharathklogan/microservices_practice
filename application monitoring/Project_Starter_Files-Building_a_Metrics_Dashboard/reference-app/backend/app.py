from flask import Flask, render_template, request, jsonify, Blueprint
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_prometheus_metrics import register_metrics
import pymongo
from pymongo import MongoClient
from flask_pymongo import PyMongo

from jaeger_client import Config
from flask_opentracing import FlaskTracing

app = Flask(__name__)
#client = MongoClient('localhost', 27017)
#db = client['example-mongodb']
app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_USERNAME'] = 'root'
app.config['MONGO_PASSWORD'] = 'password1'
app.config['MONGO_AUTH_SOURCE'] = 'admin'
app.config['MONGO_URI'] = 'mongodb://root:password1@mongo-release-mongodb.default.svc.cluster.local:27017/example-mongodb'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/example-mongodb'

config = Config(
    config={
        'sampler':
        {'type': 'const',
         'param': 1},
                        'logging': True,
                        'reporter_batch_size': 1,},
                        service_name="service-backend")
jaeger_tracer = config.initialize_tracer()
tracing = FlaskTracing(jaeger_tracer, True, app)

mongo = PyMongo(app)


CONFIG = {"version": "v0.1.2", "config": "staging"}
MAIN = Blueprint("main", __name__)

@MAIN.route('/')
def homepage():
    return "Hello World"


@app.route('/api')
def my_api():
    answer = "something"
    return jsonify(repsonse=answer)

@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  input_json = request.get_json(force=True)
  name = input_json['name']
  distance = input_json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})



def register_blueprints(app):
    """
    Register blueprints to the app
    """
    app.register_blueprint(MAIN)


def create_app(config):
  """
	Application factory
	"""
  register_blueprints(app)
  register_metrics(app, app_version=config["version"], app_config=config["config"])
  return app


#
# Dispatcher
#


def create_dispatcher() -> DispatcherMiddleware:
  """
	App factory for dispatcher middleware managing multiple WSGI apps
	"""
  main_app = create_app(config=CONFIG)
  return DispatcherMiddleware(main_app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ == "__main__":
    app = run_simple(
        hostname="0.0.0.0",
        port=5000,
        application=create_dispatcher(),
        use_reloader=True,
        use_debugger=True,
        use_evalex=True,
        threaded=True,
    )