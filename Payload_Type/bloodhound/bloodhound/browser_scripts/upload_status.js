function(task, responses){
    function getStatusString(entry) {
        if(entry["status_message"] !== ""){
            return entry["status_message"];
        }
        switch (entry["status"]){
            case -1:
                return "Invalid Job";
            case 0:
                return "Ready";
            case 1:
                return "Running";
            case 2:
                return "Complete";
            case 3:
                return "Canceled";
            case 4:
                return "Timed Out";
            case 5:
                return "Failed";
            case 6:
                return "Ingesting";
            case 7:
                return "Analyzing";
            case 8:
                return "Partially Complete";
            default:
                return "Unknown Status"
        }
    }
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
                for(let i = 0; i < data['data'].length; i++){
                    let currentData = data['data'][i];
                    output_table.push({
                        "start_time":{"plaintext": currentData["start_time"]},
                        "end_time": {"plaintext": currentData["end_time"]},
                        "id": {"plaintext": currentData["id"]},
                        "status": {"plaintext": getStatusString(currentData)},
                        "fetch": {"button": {
                                "name": "Fetch",
                                "type": "task",
                                "ui_feature": "bloodhound:upload_status",
                                "parameters": JSON.stringify({"id":currentData['id']})
                            }

                        },
                    })
                }
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "start_time", "type": "date", "fillWidth": true},
                                {"plaintext": "end_time", "type": "date", "fillWidth": true},
                                {"plaintext": "id", "type": "number", "fillWidth": true},
                                {"plaintext": "status", "type": "string", "fillWidth": true},
                                {"plaintext": "fetch", "type": "button", "width": 200},
                            ],
                            "rows": output_table,
                            "title": "Upload Status"
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