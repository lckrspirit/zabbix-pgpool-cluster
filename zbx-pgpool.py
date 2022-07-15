#!/bin/python3


from os import popen
from sys import argv
from json import dumps
from settings import pg_host, pg_port, pg_user, pg_base


command_args = argv[1:]
pgpool_stat_cmd = popen(f"psql -A --field-separator=',' -h {pg_host} -p {pg_port} -U {pg_user} {pg_base} -c 'show pool_nodes'").read()



def backendDiscovery():
    out = []
    for line in pgpool_stat_cmd.split("\n"):
        if (len(line.split(",")) != 1) and (("node_id" or "hostname") not in line.split(",")):
            out_dict = {}
            out_dict["{#PG_NODE}"] = line.split(",")[1]
            out.append(out_dict)
    print(dumps(out))



def backendState(backend):
    dict_title = {}
    for line in pgpool_stat_cmd.split("\n"):
        if len(line.split(",")) != 1:
            if (("node_id" or "hostname") in line.split(",")):
                for item in line.split(","):
                    dict_title[item] = ""
            else:
                indx = 0
                if line.split(",")[1] == backend:
                    for item in dict_title:
                        dict_title[item] =  line.split(",")[indx]
                        indx += 1
    print(dumps(dict_title))



def getBackends():
    out = []
    for line in pgpool_stat_cmd.split("\n"):
        if (len(line.split(",")) != 1) and (("node_id" or "hostname") not in line.split(",")):
            out.append( line.split(",")[1])
    return out



def app():
    if "discovery" in command_args:
        backendDiscovery()
    else:
        if command_args[0] in getBackends():
            backendState(command_args[0])



if __name__ == "__main__":
    app()
