from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class MarkOwnedArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="object_id",
                cli_name="object_id",
                description="Which object_id to mark as owned",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1,
                    group_name="mark_as_owned"
                )]
            ),
            CommandParameter(
                name="remove",
                cli_name="remove",
                description="Unmark and object as owned",
                type=ParameterType.Boolean,
                default_value=False,
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=1,
                    group_name="mark_as_owned"
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class MarkOwned(CommandBase):
    cmd = "mark_owned"
    needs_admin = False
    help_cmd = "mark_owned -object_id [object id]"
    description = "Get information about owned objects"
    version = 1
    author = "@its_a_feature_"
    argument_class = MarkOwnedArguments
    supported_ui_features = ["bloodhound:mark_owned"]
    # browser_script = BrowserScript(script_name="get_owned", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
        )
        if taskData.args.get_arg("remove"):
            response.DisplayParams = f" remove {taskData.args.get_arg('object_id')}"
        else:
            response.DisplayParams = f" {taskData.args.get_arg('object_id')}"
        try:
            owned_id = await BloodhoundAPI.get_owned_id(taskData)
            uri = f"/api/v2/asset-groups/{owned_id}/selectors"
            body = json.dumps([{"action": "add" if not taskData.args.get_arg("remove") else "remove",
                                "selector_name": taskData.args.get_arg("object_id"),
                                "sid": taskData.args.get_arg("object_id")}]).encode()
            response_code, response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                method='PUT',
                                                                                uri=uri,
                                                                                body=body)
            return await BloodhoundAPI.process_standard_response(response_code=response_code,
                                                                 response_data=response_data,
                                                                 taskData=taskData,
                                                                 response=response)

        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"{e}".encode("UTF8"),
            ))
            response.TaskStatus = "Error: Bloodhound Access Error"
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
