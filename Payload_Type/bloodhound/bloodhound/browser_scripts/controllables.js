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
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "name":{"plaintext": data[i]["name"],  "copyIcon": true},
                        "type": {"plaintext": data[i]["label"]},
                        "object_id": {"plaintext": data[i]["objectID"], "copyIcon": true},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": data[i],
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing Object Data"
                                    },
                                    {
                                        "name": "Get Object Info",
                                        "type": "task",
                                        "parameters": JSON.stringify({"object_id": data[i]["objectID"]}),
                                        "ui_feature": "bloodhound:get_object"
                                    },
                                    {
                                        "name": "Mark As Owned",
                                        "type": "task",
                                        "ui_feature": "bloodhound:mark_owned",
                                        "parameters": {"object_id": data[i]["objectID"]},
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