+++
title = "cypher_create_saved"
chapter = false
weight = 103
hidden = false
+++

## Summary

Create a new saved cypher query.

### Arguments (Positional or Popup)


#### query
The Cypher query to save

#### name
The name to use for the cypher query

## Usage
```
cypher_create_saved -query \"MATCH (n:User)WHERE n.hasspn=true RETURN n\" -name "my special query"
```