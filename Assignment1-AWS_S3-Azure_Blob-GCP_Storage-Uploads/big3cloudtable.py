from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
table_service = TableService(account_name='big3cloudproviders-sam', account_key='2T35sKxPEEs7iZ1xaVcLtTr8boburNY6jCvPfKrIjEq9F2mo3pIWscpKTU2SMzT2tLm1pljzq8yWtYUpAQ9v9g==')
table_service.create_table('bigcloud3')

task = Entity()
task.PartitionKey = 'companypartition'
task.RowKey = '101'
task.description = 'AWS'
task.priority = 100
table_service.insert_entity('companypartition', task)
print("hello")

