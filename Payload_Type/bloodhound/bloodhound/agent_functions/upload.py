from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class UploadArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file", cli_name="new-file", display_name="File to upload", type=ParameterType.File,
                description="Select new file to upload",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=True,
                        group_name="Default",
                        ui_position=0
                    )
                ]
            ),
            CommandParameter(
                name="filename", display_name="Filename within Mythic",
                description="Supply existing filename in Mythic to upload",
                type=ParameterType.ChooseOne,
                dynamic_query_function=self.get_files,
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=True,
                        ui_position=0,
                        group_name="specify already uploaded file by name"
                    )
                ]
            ),

        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)

    async def get_files(self, callback: PTRPCDynamicQueryFunctionMessage) -> PTRPCDynamicQueryFunctionMessageResponse:
        response = PTRPCDynamicQueryFunctionMessageResponse()
        file_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
            CallbackID=callback.Callback,
            LimitByCallback=False,
            IsDownloadFromAgent=True,
            IsScreenshot=False,
            IsPayload=False,
            Filename="",
        ))
        if file_resp.Success:
            file_names = []
            for f in file_resp.Files:
                if f.Filename not in file_names:
                    file_names.append(f.Filename)
            response.Success = True
            response.Choices = file_names
            return response
        else:
            await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                CallbackId=callback.Callback,
                Message=f"Failed to get files: {file_resp.Error}",
                MessageLevel="warning"
            ))
            response.Error = f"Failed to get files: {file_resp.Error}"
            return response


class Upload(CommandBase):
    cmd = "upload"
    needs_admin = False
    help_cmd = "upload -filename bloodhound.zip"
    description = "Upload a file into Bloodhound for processing"
    version = 1
    author = "@its_a_feature_"
    argument_class = UploadArguments
    supported_ui_features = ["bloodhound:upload"]
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
        )
        uri = f"/api/v2/file-upload/start"
        try:
            response_code, response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                method='POST',
                                                                                uri=uri)
            if response_code != 201:
                return await BloodhoundAPI.process_standard_response(response_code=response_code,
                                                                     response_data=response_data,
                                                                     taskData=taskData,
                                                                     response=response)
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Starting file upload with ID: {response_data['data']['id']}\n".encode("UTF8")
            ))
            fileUploadURI = f"/api/v2/file-upload/{response_data['data']['id']}"
            filename, fileContents = await self.get_file_contents(taskData)
            if len(fileContents) == 0:
                response.TaskStatus = "Error: Failed to get file contents"
                return response
            response.DisplayParams = filename
            upload_response_code, upload_response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                              method="POST",
                                                                                              uri=fileUploadURI,
                                                                                              body=fileContents)
            if upload_response_code != 202:
                return await BloodhoundAPI.process_standard_response(response_code=upload_response_code,
                                                                     response_data=upload_response_data,
                                                                     taskData=taskData,
                                                                     response=response)
            finalURI = f"{fileUploadURI}/end"
            final_response_code, final_response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                            method="POST",
                                                                                            uri=finalURI)
            if final_response_code == 200:
                await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                    TaskID=taskData.Task.ID,
                    Response=f"Successfully uploaded file and ended stream".encode("UTF8"),
                ))
                response.Success = True
                return response
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Failed to finish final transfer: {final_response_data}".encode("UTF8"),
            ))

        except Exception as e:
            logger.exception(e)
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"{e}".encode("UTF8"),
            ))
            response.TaskStatus = "Error: Bloodhound Access Error"
        return response

    async def get_file_contents(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> (str, bytes):
        groupName = taskData.args.get_parameter_group_name()
        if groupName == "Default":
            filename_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                TaskID=taskData.Task.ID,
                AgentFileID=taskData.args.get_arg("file"),
            ))
            if filename_resp.Success:
                if len(filename_resp.Files) > 0:

                    file_resp = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(
                        AgentFileId=taskData.args.get_arg("file")
                    ))
                    if not file_resp.Success:
                        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                            TaskID=taskData.Task.ID,
                            Response=f"{file_resp.Error}".encode("UTF8")
                        ))
                        return filename_resp.Files[0].Filename, b""
                    return filename_resp.Files[0].Filename, file_resp.Content
                return "", b""
            return "", b""
        file_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
            TaskID=taskData.Task.ID,
            Filename=taskData.args.get_arg("filename"),
            LimitByCallback=False,
            MaxResults=1,
            IsDownloadFromAgent=True,
            IsScreenshot=False,
            IsPayload=False,
        ))
        if file_resp.Success:
            if len(file_resp.Files) > 0:
                old_file_resp = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(
                    AgentFileId=file_resp.Files[0].AgentFileId
                ))
                return taskData.args.get_arg("filename"), old_file_resp.Content
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Failed to find that file by name, no results".encode("UTF8")
            ))
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=f"{file_resp.Error}".encode("UTF8")
        ))
        return taskData.args.get_arg("filename"), b""

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
