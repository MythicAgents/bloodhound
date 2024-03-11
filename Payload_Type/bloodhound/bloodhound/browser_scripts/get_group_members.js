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
                        "object_id":{"plaintext": data[i]["objectID"],  "copyIcon": true},
                        "name": {"plaintext": data[i]["name"]},
                        "label": {"plaintext": data[i]["label"], "copyIcon": true},
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
                                        "name": "Mark As Owned",
                                        "type": "task",
                                        "ui_feature": "bloodhound:mark_owned",
                                        "parameters": {"object_id": data[i]["objectID"], "remove": false},
                                        "startIcon": "kill"
                                    },
                                    {
                                        "name": "Get Object Information",
                                        "type": "task",
                                        "ui_feature": "bloodhound:get_object",
                                        "parameters": {"object_id": data[i]["objectID"]}
                                    },
                                    {
                                        "name": `Get ${data[i]["label"].toLowerCase()}'s Memberships`,
                                        "type": "task",
                                        "ui_feature": `bloodhound:get_${data[i]["label"].toLowerCase()}_memberships`,
                                        "parameters": {"object_id": data[i]["objectID"]}
                                    }
                                ]
                            }},
                    })
                }
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "object_id", "type": "string", "fillWidth": true},
                                {"plaintext": "name", "type": "string", "fillWidth": true},
                                {"plaintext": "label", "type": "string", "width": 100},
                                {"plaintext": "actions", "type": "button", "width": 100},
                            ],
                            "rows": output_table,
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