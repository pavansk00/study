import redis
from redis.exceptions import ConnectionError
from config import REDIS_CONFIG  # Import the REDIS_CONFIG dictionary from config.py

def redis_connect(data=None):
    try:
        # Create a Redis connection
        client = redis.Redis(
            host=REDIS_CONFIG['host'],
            port=REDIS_CONFIG['port'],
            db=REDIS_CONFIG['db'],
            password=REDIS_CONFIG['password']  # Include the password
        )

        # Test the connection
        client.ping()
        print("Connected to Redis server")

        # Example: Set and Get a value
        #client.set('key', 'value')
        if data:
            pipe = client.pipeline()
            client.set('ggggdata', data)
            #for entry in data:
                # Use the 'id' as a unique key for the hash
            #    client.hset(f"user:{entry['id']}", mapping=entry)

            # Optionally retrieve the stored data for verification
            #client.hset("mysql_data", data)
            mydata = client.get("ggggdata")
            print(mydata)
            print("====================")
        client.hset('user:1001', mapping={'name': 'Alice', 'age': 30})  # Storing fields in a hash
        name = client.hget('user:1001', 'name')# Retrieving a specific field
        print(name)
        age = client.hget('user:1001', 'age')                           # Retrieving another specific field
        print(age)
        value = client.hgetall('user:1001')
        print(f"Value for 'pavan': {value}")  # Decode bytes to string

    except ConnectionError as e:
        print(f"Error: {e}")
