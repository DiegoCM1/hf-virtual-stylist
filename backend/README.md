# Start image creation
## call once and store JSON
curl -s http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"HF-001","color_id":"Navy","cuts":["recto","cruzado"],"quality":"preview"}' > out.json

## extract recto
jq -r '.images[0].url' out.json | sed 's|^data:image/png;base64,||' | base64 -d > recto.png
## extract cruzado
jq -r '.images[1].url' out.json | sed 's|^data:image/png;base64,||' | base64 -d > cruzado.png



------

curl -s http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"family_id":"HF-001","color_id":"Navy","cuts":["recto","cruzado"],"quality":"preview","seed":123456789}' | jq .

<!-- Run backend -->
uvicorn app.main:app --reload --port 8000
