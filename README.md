# hyperion rest server

## JSON format

### DB version

Request:

```
curl http://127.0.0.1:5000/api/v1/resources/drugs/all
```

Response:

```json
[
  {
    "version": "1"
  }
]

```

### All drugs

Request:

```
curl http://127.0.0.1:5000/api/v1/resources/dbversion
```

Response:

```json
[
  {
    "drugname": "Zolpidem", 
    "id": 1344, 
    "rodrugname": null
  }, 
  {
    "drugname": "Zonisamide", 
    "id": 1345, 
    "rodrugname": null
  }
]

```

### Interaction checker

Request:

```
curl http://127.0.0.1:5000/api/v1/resources/drugs?list=macimorelin,naproxen,metformin
```

Response:

```json
[
  {
    "drug1name": "Macimorelin", 
    "drug2name": "Naproxen", 
    "interactioncode": 2
  }, 
  {
    "drug1name": "Naproxen", 
    "drug2name": "Metformin", 
    "interactioncode": 2
  }
]
```
