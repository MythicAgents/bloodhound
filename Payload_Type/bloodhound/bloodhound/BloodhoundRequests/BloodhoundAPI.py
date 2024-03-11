from mythic_container.MythicCommandBase import *
from bloodhound.BloodhoundRequests.BloodhoundAPIClasses import *
from mythic_container.MythicRPC import *

cachedAssetGroupOwnedID = None
BLOODHOUND_API_KEY = "BLOODHOUND_API_KEY"
BLOODHOUND_API_ID = "BLOODHOUND_API_ID"


def checkValidValues(token_id, token_key, url) -> bool:
    if token_id == "" or token_id is None:
        return False
    if token_key == "" or token_key is None:
        return False
    if url == "" or url is None:
        return False
    return True


async def query_bloodhound(taskData: PTTaskMessageAllData, uri: str, method: str = 'GET', body: bytes = None, ) -> \
        (int, dict):
    token_id = None
    token_key = None
    url = None
    for buildParam in taskData.BuildParameters:
        if buildParam.Name == "URL":
            url = buildParam.Value
    if BLOODHOUND_API_KEY in taskData.Secrets:
        token_key = taskData.Secrets[BLOODHOUND_API_KEY]
    if BLOODHOUND_API_ID in taskData.Secrets:
        token_id = taskData.Secrets[BLOODHOUND_API_ID]
    if not checkValidValues(token_id, token_key, url):
        if token_id == "" or token_id is None:
            return 500, "Missing BLOODHOUND_API_ID in user's secrets"
        if token_key == "" or token_key is None:
            return 500, "Missing BLOODHOUND_API_KEY in user's secrets"
        if url == "" or url is None:
            return 500, "Missing URL from build parameters"

    try:
        credentials = Credentials(token_id=token_id, token_key=token_key)
        client = Client(url=url, credentials=credentials)
        response = client.Request(method=method, uri=uri, body=body)
        logger.info(f"Bloodhound Query: {uri}")
        #logger.info(response.status_code)
        #logger.info(response.text)
        if 200 <= response.status_code < 300:
            try:
                payload = response.json()
                return response.status_code, payload
            except Exception as mid_exception:
                logger.error(mid_exception)
                return response.status_code, response.text
        else:
            return response.status_code, response.text
    except Exception as e:
        logger.exception(f"[-] Failed to query Bloodhound: \n{e}\n")
        raise Exception(f"[-] Failed to query Bloodhound: \n{e}\n")


async def get_owned_id(taskData: PTTaskMessageAllData) -> int:
    global cachedAssetGroupOwnedID

    if cachedAssetGroupOwnedID is not None:
        return cachedAssetGroupOwnedID
    uri = f"/api/v2/asset-groups"
    try:
        response_code, response_data = await query_bloodhound(taskData, method='GET', uri=uri)
        if response_code == 200:
            asset_groups = response_data["data"]
            if len(asset_groups) == 0:
                raise Exception("no asset groups")
            for x in asset_groups["asset_groups"]:
                if x["system_group"] and x["tag"] == "owned":
                    cachedAssetGroupOwnedID = x["id"]
                    return cachedAssetGroupOwnedID
            raise Exception("no owned asset_group")
        raise Exception("Failed to query")
    except Exception as e:
        raise e


async def get_whoami(taskData: PTTaskMessageAllData) -> str:
    uri = f"/api/v2/self"
    try:
        response_code, response_data = await query_bloodhound(taskData, method='GET', uri=uri)
        if response_code == 200:
            return response_data["data"]["id"]
        raise Exception("Failed to query self")
    except Exception as e:
        raise e


async def get_saved_queries(taskData: PTTaskMessageAllData) -> list[dict]:
    try:
        user_id = await get_whoami(taskData=taskData)
        uri = f"/api/v2/saved-queries?sort_by=name&user_id={user_id}"
        response_code, response_data = await query_bloodhound(taskData, method='GET', uri=uri)
        if response_code == 200:
            return response_data["data"]
        raise Exception("Failed to query")
    except Exception as e:
        raise e


async def process_standard_response(response_code: int, response_data: any,
                                    taskData: PTTaskMessageAllData, response: PTTaskCreateTaskingMessageResponse) -> \
        PTTaskCreateTaskingMessageResponse:
    if 200 <= response_code < 300:
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=json.dumps(response_data["data"]).encode("UTF8"),
        ))
        response.Success = True
    else:
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=f"{response_data}".encode("UTF8"),
        ))
        response.TaskStatus = "Error: Bloodhound Query Error"
    return response
