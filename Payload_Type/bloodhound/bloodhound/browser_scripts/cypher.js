function(task, responses){
    function colorMapping(kind){
        const round = {"border": "3px solid black",
            "color": "#000000",
            "borderRadius":"50%"};
        switch(kind){
            case "Group":
                return {...round, "backgroundColor": "rgb(210, 228, 22)"};
            case "User":
                return {...round, "backgroundColor": "rgb(36, 230, 29)"};
            case "Computer":
                return {...round, "backgroundColor": "rgb(221, 98, 96)"};
            case "Container":
                return {...round, "backgroundColor": "rgb(242, 135, 101)"};
            case "Domain":
                return {...round, "backgroundColor": "rgb(35, 228, 170)"};
            case "OU":
                return {...round, "backgroundColor": "rgb(253, 155, 10)"};
            case "GPO":
                return {...round, "backgroundColor": "rgb(134, 116, 253)"};
            case "TierZero":
                return {"border": "2px solid black", "borderRadius": "50%", "backgroundColor": "black", "color": "white"};
            case "Owned":
                return {"border": "2px solid black", "borderRadius": "50%", "backgroundColor": "black", "color": "red"};
            default:
                return {...round, "backgroundColor": "white", "color": "black"};
        }
    }
    function iconMapping(kind){
        switch(kind){
            case "Group":
                return "group";
            case "User":
                return "user";
            case "Computer":
                return "computer";
            case "Container":
                return "container";
            case "Domain":
                return "language";
            case "OU":
                return "lan";
            case "GPO":
                return "list";
            case "TierZero":
                return "diamond";
            case "Owned":
                return "skull";
            case "overlay":
                return "";
            default:
                return "help";
        }
    }
    function edgeColor(kind){
        switch(kind){
            case "MemberOf":
            case "Contains":
            case "TrustedBy":
                return "success";
            case "GenericAll":
            case "GenericWrite":
            case "HasSession":
            case "WriteDacl":
            case "AddKeyCredentialLink":
            case "WriteOwner":
                return "warning";
            default:
                return "info";
        }
    }
    function getAnimateEdge(kind){
        if(edgeColor(kind) === "success"){
            return true;
        }
        return false;
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
                let nodes = [];
                for(const [key, val] of Object.entries(data["nodes"])){
                    let tier0 = val?.["properties"]?.["system_tags"]?.includes("admin_tier_0") || false;
                    if(!tier0){
                        tier0 = val?.["isTierZero"] || false;
                    }
                    let owned = val?.["properties"]?.["system_tags"]?.includes("owned") || false;
                    let overlayImg = "overlay";
                    if(tier0){overlayImg = "TierZero"}
                    if(owned){overlayImg = "Owned"}
                    let buttons = [
                        {
                            "name": "Mark As Owned",
                            "type": "task",
                            "ui_feature": "bloodhound:mark_owned",
                            "parameters": {"object_id": val["objectId"]},
                            "startIcon": "kill"
                        },
                        {
                            "name": "Shortest Path To Here",
                            "type": "task",
                            "ui_feature": "bloodhound:shortest_path",
                            "parameters": {"end_node": val["objectId"]},
                        },
                        {
                            "name": "Shortest Path From Here",
                            "type": "task",
                            "ui_feature": "bloodhound:shortest_path",
                            "parameters": {"start_node": val["objectId"]},
                        }
                    ];
                    if(val?.properties?.hasspn && val?.properties?.serviceprincipalnames?.length > 0){
                        val?.properties?.serviceprincipalnames.forEach( (v) => {
                            buttons.push(
                                {
                                    "name": "Kerberoast " + v,
                                    "type": "task",
                                    "ui_feature": "bloodhound:kerberoast",
                                    "parameters": {
                                        "serviceprincipalname": v,
                                    },
                                    selectCallback: true,
                                    openDialog: true,
                                }
                            )
                        })

                    }
                    nodes.push({
                        id: key,
                        img: iconMapping(val["kind"]),
                        style: colorMapping(val["kind"]),
                        overlay_img: iconMapping(overlayImg),
                        overlay_style: colorMapping(overlayImg),
                        data: {...val },
                        buttons: buttons
                    })
                }
                let edges = data["edges"].map( e => {
                    let sData = data["nodes"][e["source"]];
                    sData["id"] = e["source"];
                    let dData = data["nodes"][e["target"]];
                    dData["id"] = e["target"];
                    return {
                        source: sData,
                        destination: dData,
                        label: e["label"],
                        data: {
                            kind: e["kind"],
                            lastSeen: e["lastSeen"],
                        },
                        animate: getAnimateEdge(e["kind"]),
                        color: edgeColor(e["kind"]),
                        buttons: [
                            {
                                "name": "Abuse Edge",
                                "type": "task",
                                "ui_feature": `bloodhound:${e['kind']}`.toLowerCase(),
                                "parameters": {"edge": e["kind"], "source": sData["label"], "destination": dData["label"]},
                                "startIcon": "kill",
                                selectCallback: true,
                                openDialog: true,
                            }
                        ]
                    }
                });

                return {
                    "graph": {
                        nodes: nodes,
                        edges: edges,
                        group_by: ""
                    }
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