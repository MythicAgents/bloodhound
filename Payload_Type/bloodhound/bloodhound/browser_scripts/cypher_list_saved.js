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
                        "cypher": {"plaintext": data[i]["query"]},
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
                                        "name": "Run Query",
                                        "type": "task",
                                        "parameters": JSON.stringify({"query": data[i]["query"]}),
                                        "ui_feature": "bloodhound:cypher"
                                    },
                                    {
                                        "name": "Delete Query",
                                        "type": "task",
                                        "ui_feature": "bloodhound:cypher_delete_saved",
                                        "parameters": {"query_id": data[i]["id"]},
                                        "startIcon": "kill",
                                        "getConfirmation": true,
                                    }
                                ]
                            }},
                    })
                }
                output_table.push({
                    "name": "",
                    "query": "",
                    "actions": {"button": {
                            "name": "Save New Query",
                            "type": "task",
                            "ui_feature": "bloodhound:cypher_create_saved",
                            "openDialog": true,
                        }}
                })
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "name", "type": "string", "fillWidth": true},
                                {"plaintext": "cypher", "type": "string", "fillWidth": true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Saved Cypher Queries"
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