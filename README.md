# hyperion rest server

## JSON format

### DB version

Request:

```
curl http://127.0.0.1:5000/api/v1/resources/dbversion
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
curl http://127.0.0.1:5000/api/v1/resources/drugs/all
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

### Drug-Drug interaction prediction

Request:

```
curl http://127.0.0.1:5000/api/v1/resources/scores?list=macimorelin,metformin
```

Response:

```json
[
    {
	"dbid1":"DB13074",
	"dbid2":"DB00331",
	"drugname1":"macimorelin",
	"drugname2":"metformin",
	"mild_score":
	    {
		"high":13.015819058980911,
		"low":0,
		"medium":0
	    },
	"moderate_score":
	    {
		"high":13.087586916787519,
		"low":0,
		"medium":0
	    },
	"severe_score":
	    {
		"high":0,
		"low":0.1956186206621379,
		"medium":0
	    }
    }
]
```

