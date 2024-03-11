+++
title = "cypher"
chapter = false
weight = 103
hidden = false
+++

## Summary

Execute an arbitrary Cypher query within bloodhound and view the results as a graph.

### Arguments (Positional or Popup)


#### query
The Cypher query to execute

## Usage
```
cypher -query \"MATCH (n:User)WHERE n.hasspn=true RETURN n\"
```