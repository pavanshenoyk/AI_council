config={
    "agents":[
        {
            "name":"test_agent",
            "type":"self",
            "path":"",  #anything goes but keep the folder name with the agent in it the same
            "interactive":False,  #auto,interactive
            "API":False, #add the api url if true
            "api_url":"",
            "enable":True,
            "weight_only":False
        }
    ],

    "database":"mongodb", #only mongodb for now will be adding more later
    "db_url":"",
    "db_name":"Spark_DB",
    "context_collection":"project"
}

