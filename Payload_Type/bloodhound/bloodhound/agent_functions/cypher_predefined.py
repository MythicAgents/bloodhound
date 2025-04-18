from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class CypherPredefinedArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="query_name",
                cli_name="query-name",
                description="Run a predefined cypher query from Bloodhound CE",
                type=ParameterType.ChooseOne,
                default_value="All Domain Admins",
                choices=list(predefined_queries.keys()),
                parameter_group_info=[ParameterGroupInfo(
                    required=True
                )]
            )
        ]

    async def parse_arguments(self):
        return self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        return self.load_args_from_dictionary(dictionary=dictionary_arguments)


predefined_queries = {
    "All Domain Admins": """
MATCH p = (t:Group)<-[:MemberOf*1..]-(a)
WHERE (a:User or a:Computer) and t.objectid ENDS WITH '-512'
RETURN p
LIMIT 1000
    """,
    "Map domain trusts": """
MATCH p = (:Domain)-[:TrustedBy]->(:Domain)
RETURN p
LIMIT 1000
    """,
    "Locations of Tier Zero / High Value objects": """
MATCH p = (t:Base)<-[:Contains*1..]-(:Domain)
WHERE COALESCE(t.system_tags, '') CONTAINS 'admin_tier_0'
RETURN p
LIMIT 1000
    """,
    "Map OU structure": """
MATCH p = (:Domain)-[:Contains*1..]->(:OU)
RETURN p
LIMIT 1000
    """,
    "Principals with DCSync privileges": """
MATCH p=(:Base)-[:DCSync|AllExtendedRights|GenericAll]->(:Domain)
RETURN p
LIMIT 1000
    """,
    "Principals with foreign domain group membership": """
MATCH p=(s:Base)-[:MemberOf]->(t:Group)
WHERE s.domainsid<>t.domainsid
RETURN p
LIMIT 1000
    """,
    "Computers where Domain Users are local administrators": """
MATCH p=(s:Group)-[:AdminTo]->(:Computer)
WHERE s.objectid ENDS WITH '-513'
RETURN p
LIMIT 1000
    """,
    "Computers where Domain Users can read LAPS passwords": """
MATCH p=(s:Group)-[:AllExtendedRights|ReadLAPSPassword]->(:Computer)
WHERE s.objectid ENDS WITH '-513'
RETURN p
LIMIT 1000   
    """,
    "Paths from Domain Users to Tier Zero / High Value targets": """
MATCH p=shortestPath((s:Group)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|GPLink|AllowedToDelegate|CoerceToTGT|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|WriteGPLink|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|SyncedToEntraUser|CoerceAndRelayNTLMToSMB|CoerceAndRelayNTLMToADCS|WriteOwnerLimitedRights|OwnsLimitedRights|CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|Contains|DCFor|TrustedBy*1..]->(t))
WHERE COALESCE(t.system_tags, '') CONTAINS 'admin_tier_0' AND s.objectid ENDS WITH '-513' AND s<>t
RETURN p
LIMIT 1000  
    """,
    "Workstations where Domain Users can RDP": """
MATCH p=(s:Group)-[:CanRDP]->(t:Computer)
WHERE s.objectid ENDS WITH '-513' AND NOT toUpper(t.operatingsystem) CONTAINS 'SERVER'
RETURN p
LIMIT 1000 
    """,
    "Servers where Domain Users can RDP": """
MATCH p=(s:Group)-[:CanRDP]->(t:Computer)
WHERE s.objectid ENDS WITH '-513' AND toUpper(t.operatingsystem) CONTAINS 'SERVER'
RETURN p
LIMIT 1000   
    """,
    "Dangerous privileges for Domain Users groups": """
MATCH p=(s:Group)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|GPLink|AllowedToDelegate|CoerceToTGT|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|WriteGPLink|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|SyncedToEntraUser|CoerceAndRelayNTLMToSMB|CoerceAndRelayNTLMToADCS|WriteOwnerLimitedRights|OwnsLimitedRights|CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|Contains|DCFor|TrustedBy]->(:Base)
WHERE s.objectid ENDS WITH '-513'
RETURN p
LIMIT 1000 
    """,
    "Domain Admins logons to non-Domain Controllers": """
MATCH (s)-[:MemberOf*0..]->(g:Group)
WHERE g.objectid ENDS WITH '-516'
WITH COLLECT(s) AS exclude
MATCH p = (c:Computer)-[:HasSession]->(:User)-[:MemberOf*1..]->(g:Group)
WHERE g.objectid ENDS WITH '-512' AND NOT c IN exclude
RETURN p
LIMIT 1000  
    """,
    "Kerberoastable members of Tier Zero / High Value groups": """
MATCH (u:User)
WHERE u.hasspn=true
AND u.enabled = true
AND NOT u.objectid ENDS WITH '-502'
AND NOT COALESCE(u.gmsa, false) = true
AND NOT COALESCE(u.msa, false) = true
AND COALESCE(u.system_tags, '') CONTAINS 'admin_tier_0'
RETURN u
LIMIT 100   
    """,
    "All Kerberoastable users": """
MATCH (u:User)
WHERE u.hasspn=true
AND u.enabled = true
AND NOT u.objectid ENDS WITH '-502'
AND NOT COALESCE(u.gmsa, false) = true
AND NOT COALESCE(u.msa, false) = true
RETURN u
LIMIT 100  
    """,
    "Kerberoastable users with most privileges": """
MATCH (u:User)
WHERE u.hasspn = true
  AND u.enabled = true
  AND NOT u.objectid ENDS WITH '-502'
  AND NOT COALESCE(u.gmsa, false) = true
  AND NOT COALESCE(u.msa, false) = true
MATCH (u)-[:MemberOf|AdminTo*1..]->(c:Computer)
WITH DISTINCT u, COUNT(c) AS adminCount
RETURN u
ORDER BY adminCount DESC
LIMIT 100 
    """,
    "AS-REP Roastable users (DontReqPreAuth)": """
MATCH (u:User)
WHERE u.dontreqpreauth = true
AND u.enabled = true
RETURN u
LIMIT 100  
    """,
    "Shortest paths to systems trusted for unconstrained delegation": """
MATCH p=shortestPath((s)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|GPLink|AllowedToDelegate|CoerceToTGT|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|WriteGPLink|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|SyncedToEntraUser|CoerceAndRelayNTLMToSMB|CoerceAndRelayNTLMToADCS|WriteOwnerLimitedRights|OwnsLimitedRights|CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|Contains|DCFor|TrustedBy*1..]->(t:Computer))
WHERE t.unconstraineddelegation = true AND s<>t
RETURN p
LIMIT 1000 
    """,
    "Shortest paths to Domain Admins from Kerberoastable users": """
MATCH p=shortestPath((s:User)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|GPLink|AllowedToDelegate|CoerceToTGT|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|WriteGPLink|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|SyncedToEntraUser|CoerceAndRelayNTLMToSMB|CoerceAndRelayNTLMToADCS|WriteOwnerLimitedRights|OwnsLimitedRights|CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|Contains|DCFor|TrustedBy*1..]->(t:Group))
WHERE s.hasspn=true
AND s.enabled = true
AND NOT s.objectid ENDS WITH '-502'
AND NOT COALESCE(s.gmsa, false) = true
AND NOT COALESCE(s.msa, false) = true
AND t.objectid ENDS WITH '-512'
RETURN p
LIMIT 1000   
    """,
    "Shortest paths to Tier Zero / High Value targets": """
MATCH p=shortestPath((s)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|GPLink|AllowedToDelegate|CoerceToTGT|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|WriteGPLink|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|SyncedToEntraUser|CoerceAndRelayNTLMToSMB|CoerceAndRelayNTLMToADCS|WriteOwnerLimitedRights|OwnsLimitedRights|CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|Contains|DCFor|TrustedBy*1..]->(t))
WHERE COALESCE(t.system_tags, '') CONTAINS 'admin_tier_0' AND s<>t
RETURN p
LIMIT 1000 
    """,
    "Shortest paths from Domain Users to Tier Zero / High Value targets": """
MATCH p=shortestPath((s:Group)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|GPLink|AllowedToDelegate|CoerceToTGT|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|WriteGPLink|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|SyncedToEntraUser|CoerceAndRelayNTLMToSMB|CoerceAndRelayNTLMToADCS|WriteOwnerLimitedRights|OwnsLimitedRights|CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|Contains|DCFor|TrustedBy*1..]->(t))
WHERE COALESCE(t.system_tags, '') CONTAINS 'admin_tier_0' AND s.objectid ENDS WITH '-513' AND s<>t
RETURN p
LIMIT 1000   
    """,
    "Shortest paths to Domain Admins": """
MATCH p=shortestPath((t:Group)<-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|GPLink|AllowedToDelegate|CoerceToTGT|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|WriteGPLink|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|SyncedToEntraUser|CoerceAndRelayNTLMToSMB|CoerceAndRelayNTLMToADCS|WriteOwnerLimitedRights|OwnsLimitedRights|CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|Contains|DCFor|TrustedBy*1..]-(s:Base))
WHERE t.objectid ENDS WITH '-512' AND s<>t
RETURN p
LIMIT 1000   
    """,
    "Shortest paths from Owned objects": """
MATCH p=shortestPath((s:Base)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|GPLink|AllowedToDelegate|CoerceToTGT|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|WriteGPLink|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC6a|ADCSESC6b|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|SyncedToEntraUser|CoerceAndRelayNTLMToSMB|CoerceAndRelayNTLMToADCS|WriteOwnerLimitedRights|OwnsLimitedRights|CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|Contains|DCFor|TrustedBy*1..]->(t:Base))
WHERE COALESCE(s.system_tags, '') CONTAINS 'owned' AND s<>t
RETURN p
LIMIT 1000
    """,
    "PKI hierarchy": """
MATCH p=()-[:HostsCAService|IssuedSignedBy|EnterpriseCAFor|RootCAFor|TrustedForNTAuth|NTAuthStoreFor*..]->(:Domain)
RETURN p
LIMIT 1000
    """,
    "Public Key Services container": """
MATCH p = (c:Container)-[:Contains*..]->(:Base)
WHERE c.distinguishedname starts with 'CN=PUBLIC KEY SERVICES,CN=SERVICES,CN=CONFIGURATION,DC='
RETURN p
LIMIT 1000 
    """,
    "Enrollment rights on published certificate templates": """
MATCH p = (:Base)-[:Enroll|GenericAll|AllExtendedRights]->(:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
RETURN p
LIMIT 1000
    """,
    "Enrollment rights on published ESC1 certificate templates": """
MATCH p = (:Base)-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
WHERE ct.enrolleesuppliessubject = True
AND ct.authenticationenabled = True
AND ct.requiresmanagerapproval = False
AND (ct.authorizedsignatures = 0 OR ct.schemaversion = 1)
RETURN p
LIMIT 1000 
    """,
    "Enrollment rights on published ESC2 certificate templates": """
MATCH p = (:Base)-[:Enroll|GenericAll|AllExtendedRights]->(c:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
WHERE c.requiresmanagerapproval = false
AND (c.effectiveekus = [''] OR '2.5.29.37.0' IN c.effectiveekus)
AND (c.authorizedsignatures = 0 OR c.schemaversion = 1)
RETURN p
LIMIT 1000
    """,
    "Enrollment rights on published enrollment agent certificate templates": """
MATCH p = (:Base)-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
WHERE '1.3.6.1.4.1.311.20.2.1' IN ct.effectiveekus
OR '2.5.29.37.0' IN ct.effectiveekus
OR SIZE(ct.effectiveekus) = 0
RETURN p
LIMIT 1000   
    """,
    "Enrollment rights on published certificate templates with no security extension": """
MATCH p = (:Base)-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
WHERE ct.nosecurityextension = true
RETURN p
LIMIT 1000   
    """,
    "Enrollment rights on certificate templates published to Enterprise CA with User Specified SAN enabled": """
MATCH p = (:Base)-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(eca:EnterpriseCA)
WHERE eca.isuserspecifiessanenabled = True
RETURN p
LIMIT 1000 
    """,
    "CA administrators and CA managers": """
MATCH p = (:Base)-[:ManageCertificates|ManageCA]->(:EnterpriseCA)
RETURN p
LIMIT 1000  
    """,
    "Domain controllers with weak certificate binding enabled": """
MATCH p = (s:Computer)-[:DCFor]->(:Domain)
WHERE s.strongcertificatebindingenforcementraw = 0 OR s.strongcertificatebindingenforcementraw = 1
RETURN p
LIMIT 1000 
    """,
    "Domain controllers with UPN certificate mapping enabled": """
MATCH p = (s:Computer)-[:DCFor]->(:Domain)
WHERE s.certificatemappingmethodsraw IN [4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23, 28, 29, 30, 31]
RETURN p
LIMIT 1000 
    """,
    "Non-default permissions on IssuancePolicy nodes": """
MATCH p = (s:Base)-[:GenericAll|GenericWrite|Owns|WriteOwner|WriteDacl]->(:IssuancePolicy)
WHERE NOT s.objectid ENDS WITH '-512' AND NOT s.objectid ENDS WITH '-519'
RETURN p
LIMIT 1000
    """,
    "Enrollment rights on CertTemplates with OIDGroupLink": """
MATCH p = (:Base)-[:Enroll|GenericAll|AllExtendedRights]->(:CertTemplate)-[:ExtendedByPolicy]->(:IssuancePolicy)-[:OIDGroupLink]->(:Group)
RETURN p
LIMIT 1000
""",
    "Enabled Tier Zero / High Value principals inactive for 60 days": """
WITH 60 as inactive_days
MATCH (n:Base)
WHERE COALESCE(n.system_tags, '') CONTAINS 'admin_tier_0'
AND n.enabled = true
AND n.lastlogontimestamp < (datetime().epochseconds - (inactive_days * 86400)) // Replicated value
AND n.lastlogon < (datetime().epochseconds - (inactive_days * 86400)) // Non-replicated value
AND n.whencreated < (datetime().epochseconds - (inactive_days * 86400)) // Exclude recently created principals
AND NOT n.name STARTS WITH 'AZUREADKERBEROS.' // Removes false positive, Azure KRBTGT
AND NOT n.objectid ENDS WITH '-500' // Removes false positive, built-in Administrator
AND NOT n.name STARTS WITH 'AZUREADSSOACC.' // Removes false positive, Entra Seamless SSO
RETURN n
""",
    "Tier Zero / High Value enabled users not requiring smart card authentication": """
MATCH (u:User)
WHERE COALESCE(u.system_tags, '') CONTAINS 'admin_tier_0'
AND u.enabled = true
AND u.smartcardrequired = false
AND NOT u.name STARTS WITH 'MSOL_' // Removes false positive, Entra sync
AND NOT u.name STARTS WITH 'PROVAGENTGMSA' // Removes false positive, Entra sync
AND NOT u.name STARTS WITH 'ADSYNCMSA_' // Removes false positive, Entra sync
RETURN u
    """,
    "Domains where any user can join a computer to the domain": """
MATCH (d:Domain)
WHERE d.machineaccountquota > 0
RETURN d
    """,
    "Domains with smart card accounts where smart account passwords do not expire": """
MATCH (s:Domain)-[:Contains*1..]->(t:Base)
WHERE s.expirepasswordsonsmartcardonlyaccounts = false
AND t.enabled = true
AND t.smartcardrequired = true
RETURN s
""",
    "Two-way forest trusts enabled for delegation": """
MATCH p=(n:Domain)-[r:TrustedBy]->(m:Domain)
WHERE (m)-[:TrustedBy]->(n)
AND r.trusttype = 'Forest'
AND r.tgtdelegationenabled = true
RETURN p
    """,
    "Computers with unsupported operating systems": """
MATCH (c:Computer)
WHERE c.operatingsystem =~ '(?i).*Windows.* (2000|2003|2008|2012|xp|vista|7|8|me|nt).*'
RETURN c
LIMIT 100
""",
    "Users which do not require password to authenticate": """
MATCH (u:User)
WHERE u.passwordnotreqd = true
RETURN u
LIMIT 100
""",
    "Users with passwords not rotated in over 1 year": """
WITH 365 as days_since_change
MATCH (u:User)
WHERE u.pwdlastset < (datetime().epochseconds - (days_since_change * 86400))
AND NOT u.pwdlastset IN [-1.0, 0.0]
RETURN u
LIMIT 100
""",
    "Nested groups within Tier Zero / High Value": """
MATCH p=(t:Group)<-[:MemberOf*..]-(s:Group)
WHERE COALESCE(t.system_tags, '') CONTAINS 'admin_tier_0'
AND NOT s.objectid ENDS WITH '-512' // Domain Admins
AND NOT s.objectid ENDS WITH '-519' // Enterprise Admins
RETURN p
LIMIT 1000
    """,
    "Disabled Tier Zero / High Value principals": """
MATCH (n:Base)
WHERE COALESCE(n.system_tags, '') CONTAINS 'admin_tier_0'
AND n.enabled = false
AND NOT n.objectid ENDS WITH '-502' // Removes false positive, KRBTGT
AND NOT n.objectid ENDS WITH '-500' // Removes false positive, built-in Administrator
RETURN n
LIMIT 100
    """,
    "Principals with passwords stored using reversible encryption": """
MATCH (n:Base)
WHERE n.encryptedtextpwdallowed = true
RETURN n
""",
    "Principals with DES-only Kerberos authentication": """
MATCH (n:Base)
WHERE n.enabled = true
AND n.usedeskeyonly = true
RETURN n
""",
    "Principals with weak supported Kerberos encryption types": """
MATCH (u:Base)
WHERE 'DES-CBC-CRC' IN u.supportedencryptiontypes
OR 'DES-CBC-MD5' IN u.supportedencryptiontypes
OR 'RC4-HMAC-MD5' IN u.supportedencryptiontypes
RETURN u
""",
    "Tier Zero / High Value users with non-expiring passwords": """
MATCH (u:User)
WHERE u.enabled = true
AND u.pwdneverexpires = true
and COALESCE(u.system_tags, '') CONTAINS 'admin_tier_0'
RETURN u
LIMIT 100
""",
    "All coerce and NTLM relay edges": """
MATCH p = (n:Base)-[:CoerceAndRelayNTLMToLDAP|CoerceAndRelayNTLMToLDAPS|CoerceAndRelayNTLMToADCS|CoerceAndRelayNTLMToSMB]->(:Base)
RETURN p LIMIT 500
    """,
    "ESC8-vulnerable Enterprise CAs": """
MATCH (n:EnterpriseCA)
WHERE n.hasvulnerableendpoint=true
RETURN n
""",
    "Computers with the outgoing NTLM setting set to Deny all": """
MATCH (c:Computer)
WHERE c.restrictoutboundntlm = True
RETURN c LIMIT 1000
""",
    "Computers with membership in Protected Users": """
MATCH p = (:Base)-[:MemberOf*1..]->(g:Group)
WHERE g.objectid ENDS WITH "-525"
RETURN p LIMIT 1000
""",
    "DCs vulnerable to NTLM relay to LDAP attacks": """
MATCH p = (dc:Computer)-[:DCFor]->(:Domain)
WHERE (dc.ldapavailable = True AND dc.ldapsigning = False)
OR (dc.ldapsavailable = True AND dc.ldapsepa = False)
OR (dc.ldapavailable = True AND dc.ldapsavailable = True AND dc.ldapsigning = False and dc.ldapsepa = True)
RETURN p
""",
    "Computers with the WebClient running": """
MATCH (c:Computer)
WHERE c.webclientrunning = True
RETURN c LIMIT 1000
""",
    "Computers not requiring inbound SMB signing": """
MATCH (n:Computer)
WHERE n.smbsigning = False
RETURN n
"""
}


class CypherPredefined(CommandBase):
    cmd = "cypher_predefined"
    needs_admin = False
    help_cmd = cmd
    description = "Run one of Bloodhound's predefined queries"
    version = 1
    author = "@its_a_feature_"
    argument_class = CypherPredefinedArguments
    browser_script = BrowserScript(script_name="cypher", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f"{taskData.args.get_arg('query_name')}"
        )
        uri = f"/api/v2/graphs/cypher"
        body = json.dumps({
            "include_properties": True,
            "query": predefined_queries[taskData.args.get_arg("query_name")]
        }).encode()
        response.Stdout = predefined_queries[taskData.args.get_arg("query_name")]
        try:
            response_code, response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                method='POST',
                                                                                body=body,
                                                                                uri=uri)
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
