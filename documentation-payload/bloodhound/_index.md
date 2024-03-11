+++
title = "Bloodhound"
chapter = true
weight = 100
+++

![logo](/agents/bloodhound/bloodhound.svg?width=100px)

## Summary

Bloodhound is a service agent for Mythic - it doesn't generate any payloads, but instead provides an easy interface to work with an external instance of Bloodhound Community Edition.

{{% notice info %}}
You must generate an API Token and ID in Bloodhound to use this agent. Once you've generated those in bloodhound, go to your user settings in Mythic and click the "red key" icon to configure your secrets.

BLOODHOUND_API_KEY and BLOODHOUND_API_ID are the two secret keys to configure.
{{% /notice %}}

### Highlighted Agent Features

- File Uploads to Bloodhound
- Cypher Queries (custom, saved, and all pre-defined ones in Bloodhound's UI)
- Graph Views
- Mark as Owned
  
## Authors

- [@its_a_feature_](https://twitter.com/its_a_feature_)

### Special Thanks to These Contributors

- Bloodhound Team for their API and amazing service

## Table of Contents

{{% children %}}