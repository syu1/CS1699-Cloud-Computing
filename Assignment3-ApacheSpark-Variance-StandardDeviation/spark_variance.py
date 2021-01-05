import findspark
findspark.init()
import random
import pandas as pd
import numpy as np
from pyspark.sql import Window
from pyspark.sql import Row
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import explode, col, udf, mean as _mean, stddev as _stddev
from pyspark.sql.types import *
sc = SparkContext.getOrCreate()
spark = SparkSession.builder.getOrCreate()
# mock up sample dataframe
# initalize random sample dataframe
my_list = []

def random_nums():
    for i in range(100):
        my_ran = random.randint(1,101)
        
        my_list.append((i,my_ran))

random_nums()
rdd = sc.parallelize(my_list)
rans = rdd.map(lambda x: Row(pk=x[0], rnum=int(x[1])))
my_schema = spark.createDataFrame(rans)
my_schema.show()
my_schema2 = my_schema.describe("rnum")

my_schema2.show()
my_schema2=my_schema2.rdd.take(3)

my_stdv = my_schema2[2]
my_stdv.__getattr__("summary")
final_stv= my_stdv.__getattr__("rnum")
vari = float(final_stv)*float(final_stv)
print(f"Variance is STDEV squared. Current stdv for 100 nums is {final_stv}")
print(f"Calculated Variance is {vari}")


sc.stop()