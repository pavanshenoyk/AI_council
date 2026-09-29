config={
    "agents":[
        {
            "name":"test_agent",  #anything goes but keep the folder name with the agent in it the same
            "interactive":False,  #auto,interactive
            "API":False, #add the api url if true
            "api_url":"",
            "enable":True,
            "weight_only":False
        }
    ],

    "database":"mongodb", #only mongodb for now will be adding more later
    "db_url":"mongodb://<db_username>:b2eWJBRxMnkt9FtL@ac-8ldecm6-shard-00-00.1ndsfdq.mongodb.net:27017,ac-8ldecm6-shard-00-01.1ndsfdq.mongodb.net:27017,ac-8ldecm6-shard-00-02.1ndsfdq.mongodb.net:27017/?ssl=true&replicaSet=atlas-vnay2p-shard-0&authSource=admin&appName=SparkDB",
    "db_name":"SparkDB",
    "context_size":5
}

