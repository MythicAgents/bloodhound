from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class UploadStatusArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="id",  display_name="ID returned from `upload` command", type=ParameterType.Number,
                description="Bloodhound ID from uploading the file",
                default_value=0,
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        group_name="Default",
                        ui_position=0
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


class UploadStatus(CommandBase):
    cmd = "upload_status"
    needs_admin = False
    help_cmd = "upload_status -id 6"
    description = "Check the upload/ingesting status for Bloodhound files"
    version = 1
    author = "@its_a_feature_"
    argument_class = UploadStatusArguments
    supported_ui_features = ["bloodhound:upload_status"]
    browser_script = BrowserScript(script_name="upload_status", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
        )
        uri = f"/api/v2/file-upload"
        if taskData.args.get_arg("id") > 0:
            uri += f"?limit=1&id=eq%3A{taskData.args.get_arg('id')}"
            response.DisplayParams = f"for job {taskData.args.get_arg('id')}"
        else:
            uri += f"?limit=10&sort_by=-id"
            response.DisplayParams = f" for the 10 most recent jobs"
        try:
            response_code, response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                method='GET',
                                                                                uri=uri)
            if response_code != 200:
                return await BloodhoundAPI.process_standard_response(response_code=response_code,
                                                                     response_data=response_data,
                                                                     taskData=taskData,
                                                                     response=response)
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"{json.dumps(response_data)}".encode("UTF8"),
            ))
        except Exception as e:
            logger.exception(e)
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"{e}".encode("UTF8"),
            ))
            response.TaskStatus = "Error: Bloodhound Access Error"
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
