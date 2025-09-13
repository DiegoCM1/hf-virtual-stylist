import time, uuid, random
from app.models.generate import GenerationRequest, GenerationResponse, ImageResult

class Generator:
    def generate(self, req: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError

# Let us demo end to end, able to switch to SDXL later without changing routes.
class MockGenerator(Generator): 
    def generate(self, req: GenerationRequest) -> GenerationResponse:
        t0 = time.time()
        rid = str(uuid.uuid4())[:8]
        imgs = []
        for c in req.cuts[:2]:
            # placeholder size ~1024x1536 for portrait-like
            url = f"https://picsum.photos/seed/{c}-{random.randint(1,9999)}/1024/1536"
            imgs.append(ImageResult(
                cut=c, url=url, width=1024, height=1536, watermark=True,
                meta={"mock":"true"}))
        return GenerationResponse(
            request_id=rid,
            status="completed",
            images=imgs,
            duration_ms=int((time.time()-t0)*1000),
            meta={"family_id": req.family_id, "color_id": req.color_id}
        )
