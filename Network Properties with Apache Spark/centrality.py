from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import functions
from graphframes import *
from pyspark.sql.functions import explode

sc=SparkContext("local", "degree.py")
sqlContext = SQLContext(sc)

def closeness(g):
	
	# Get list of vertices. We'll generate all the shortest paths at
	# once using this list.
	# YOUR CODE HERE

	# first get all the path lengths.
    vertices = g.vertices.flatMap(lambda x:x).collect()
    pathLengths = g.shortestPaths(landmarks = vertices)

	# Break up the map and group by ID for summing
    splitData = pathLengths.select("id", explode("distances"))
    groupData = splitData.groupBy(splitData.id)
	# Sum by ID
    sumLength = groupData.agg({"value": "sum"})
	# Get the inverses and generate desired dataframe.
    vertex_c = vertex_c.select(col("id"),col("sum(value)").alias("closeness"))
    
    result_df = vertex_c.map(lambda row: (row.id,1/float(row.closeness))).toDF().select(col("_1").alias("id"), col("_2").alias("closeness"))
    
    return result_df

    
    
    
    	# Sum by ID
    sum_path_length = path_length.groupBy('key').agg(functions.sum('value').alias('sum'))

	# Get the inverses and generate desired dataframe.
    closeness = sum_path_length.withColumn('sum', 1 / sum_path_length.sum).selectExpr('key as id', 'sum as closeness') 
    
    return closeness

print("Reading in graph for problem 2.")
graph = sc.parallelize([('A','B'),('A','C'),('A','D'),
	('B','A'),('B','C'),('B','D'),('B','E'),
	('C','A'),('C','B'),('C','D'),('C','F'),('C','H'),
	('D','A'),('D','B'),('D','C'),('D','E'),('D','F'),('D','G'),
	('E','B'),('E','D'),('E','F'),('E','G'),
	('F','C'),('F','D'),('F','E'),('F','G'),('F','H'),
	('G','D'),('G','E'),('G','F'),
	('H','C'),('H','F'),('H','I'),
	('I','H'),('I','J'),
	('J','I')])
	
e = sqlContext.createDataFrame(graph,['src','dst'])
v = e.selectExpr('src as id').unionAll(e.selectExpr('dst as id')).distinct()
print("Generating GraphFrame.")
g = GraphFrame(v,e)

print("Calculating closeness.")
closeness(g).sort('closeness',ascending=False).show()
