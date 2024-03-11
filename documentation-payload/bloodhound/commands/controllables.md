+++
title = "controllables"
chapter = false
weight = 103
hidden = false
+++

## Summary

Get the outbound control the specified object has over other objects.

### Arguments (Positional or Popup)


#### object_id
The object_id for the object to inspect - this will typically be in the form `S-1-5-21-909015691-3030120388-2582151266-512`, but not always. 
You can use the `search` feature to look for specific objects by name and get the object id from them.

## Usage
```
controllables -object_id \"S-1-5-21-909015691-3030120388-2582151266-512\"
```