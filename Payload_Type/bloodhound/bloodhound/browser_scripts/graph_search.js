function(task, responses){
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        if(responses.length > 0){
            try{
                let data = JSON.parse(responses[0]);
                let output_table = [];
                for(const[key, value] of Object.entries(data)){
                    output_table.push({
                        "name":{"plaintext": value.data["name"],  "copyIcon": true},
                        "type": {"plaintext": value.data["nodetype"]},
                        "object_id": {"plaintext": value.data["object_id"], "copyIcon": true},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": value.data,
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing Object Data"
                                    },
                                    {
                                        "name": "Controllables",
                                        "type": "task",
                                        "ui_feature": "bloodhound:controllables",
                                        "parameters": JSON.stringify({"object_id": value.data["objectid"]})
                                    },
                                    {
                                        "name": "Get Object",
                                        "type": "task",
                                        "ui_feature": "bloodhound:get_object",
                                        "parameters": JSON.stringify({"object_id": value.data["objectid"]})
                                    },
                                    {
                                        "name": "Mark As Owned",
                                        "type": "task",
                                        "ui_feature": "bloodhound:mark_owned",
                                        "parameters": {"object_id": value.data["objectid"]},
                                        "startIcon": "kill"
                                    }
                                ]
                            }},
                    })
                }
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "name", "type": "string", "fillWidth": true},
                                {"plaintext": "type", "type": "string", "width": 200},
                                {"plaintext": "object_id", "type": "string", "width": 400},
                                {"plaintext": "actions", "type": "button", "width": 100},
                            ],
                            "rows": output_table,
                            "title": "Search Results"
                        }
                    ]
                }
            }catch(error){
                console.log(error);
                const combined = responses.reduce( (prev, cur) => {
                    return prev + cur;
                }, "");
                return {'plaintext': combined};
            }
        }else{
            return {"plaintext": "No output from command"};
        }
    }else{
        return {"plaintext": "No data to display..."};
    }
}