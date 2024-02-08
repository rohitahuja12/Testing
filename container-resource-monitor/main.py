import docker
import json
import csv

client = docker.from_env()

containers = client.containers.list()
c = next(c for c in containers if "reader" in c.name)


with open('metrics.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    csvwriter.writerow([
        "timestamp", 
        "cpu_usage",
        "memory_usage",
    ])

    for stat in c.stats():
        statsobj = json.loads(stat.decode())
        csvwriter.writerow([
            statsobj['read'], 
            statsobj['cpu_stats']['cpu_usage']['total_usage'],
            statsobj['memory_stats']['usage']
        ])
