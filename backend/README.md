# Start image creation
## call once and store JSON
curl -s http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"HF-001","color_id":"Navy","cuts":["recto","cruzado"],"quality":"preview"}' > out.json

## extract recto
jq -r '.images[0].url' out.json | sed 's|^data:image/png;base64,||' | base64 -d > recto.png
## extract cruzado
jq -r '.images[1].url' out.json | sed 's|^data:image/png;base64,||' | base64 -d > cruzado.png


<!-- TESTS -->

## Testing in general
pytest -q

### Health
curl -s http://127.0.0.1:8000/healthz

Expect: {"ok":true,...}

### Generate
curl -s -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"lana-normal","color_id":"green-001"}'

Expect: images[0].url and images[1].url HTTP URLs under /files/generated/...

- URLs load (HEAD check)
```
URL1="<<paste images[0].url>>"
URL2="<<paste images[1].url>>"
curl -I "$URL1"
curl -I "$URL2"
```



<!-- Run backend -->
uvicorn app.main:app --reload --port 8000
