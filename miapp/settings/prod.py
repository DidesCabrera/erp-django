from .base import *

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "www.myscoope.com,myscoope.com,my-scoope.onrender.com"
).split(",")

