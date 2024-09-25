from database.mysql_connector import mysql_connect
from cache_redis.redis_connector import redis_connect
import json
# Call the connection function
data = mysql_connect()
data = json.dumps(data)
redis_connect(data)
