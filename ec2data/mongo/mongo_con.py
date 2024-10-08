from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne

# Use the correct host and port (default is 'localhost:27017')
client = MongoClient("mongodb://localhost:27017/")
import pdb;pdb.set_trace()
# Access the database
db = client['mydb']

# List collections
collections = db.list_collection_names()
emp = db['emp']
emp_data = [
        {'name':'vb','id':3,'city':'pune'},
        {'name':'ch','id':4,'city':'pune'}
        ]
result = emp.insert_many(emp_data)
print(result.inserted_ids)
print(collections)

all_records = emp.find()

#retrive all documents in callections
for record in all_records:
    print(record)

#find record in collection where city is pune
query = {'city':'pune'}

pune_city_data = emp.find(query)

print("pune city data")

for record in pune_city_data:
    print(record)

#update record where id =3 change to thane

update_query = {'id':3}

new_value = {'$set':{'city':'thane'}}

updated_result = emp.update_one(update_query, new_value)

print("\n Updated records count:",updated_result.modified_count)

#delete data where id is 4
import pdb;pdb.set_trace()
delete_query = {'id':4}
deleted_result = emp.delete_one(delete_query)

print("\n deleted the data related to id =4",deleted_result.deleted_count)

#creating index
emp.create_index([('id',1)])

indexes = emp.index_information()
print("index information:",indexes)

#derop index
emp.drop_index('id_1')
#emp.drop_index()  # to drop all index

#Grouping and Summing

pipeline = [
    {'$group': {'_id': '$city', 'total_employees': {'$sum': 1}}},
    {'$sort': {'total_employees': -1}}  # Sort by the total employees in descending order
]
agg_result = emp.aggregate(pipeline)
for result in agg_result:
    print(result)


req = [
        InsertOne({'name':'dk','id':5,'city':'thane'}),
        UpdateOne({'id':3}, {'$set':{'city':'pune'}}),
        DeleteOne({'id':4})
        ]
result = emp.bulk_write(req)
print("Bulk Write Results:", result.bulk_api_result)

