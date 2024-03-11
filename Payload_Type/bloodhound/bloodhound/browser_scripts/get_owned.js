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
                for(let i = 0; i < data['members'].length; i++){
                    output_table.push({
                        "name":{"plaintext": data['members'][i]["name"],  "copyIcon": true},
                        "type": {"plaintext": data['members'][i]["primary_kind"]},
                        "object_id": {"plaintext": data['members'][i]["object_id"], "copyIcon": true},
                        "environment_type": {"plaintext": data['members'][i]["environment_kind"]},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": data['members'][i],
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing Object Data"
                                    },
                                    {
                                        "name": "Remove As Owned",
                                        "type": "task",
                                        "ui_feature": "bloodhound:mark_owned",
                                        "parameters": {"object_id": data['members'][i]["object_id"], "remove": true},
                                        "startIcon": "delete"
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
                                {"plaintext": "environment_type", "type": "string", "width": 200},
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