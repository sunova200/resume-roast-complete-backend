import base64
import os
from io import BytesIO

from bson import ObjectId
from dotenv import load_dotenv
from groq import Groq
from pdf2image import convert_from_path
from PIL import Image

from ..db.collections.files import files_collection

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
MAX_IMAGES_PER_REQUEST = 5
MAX_IMAGE_WIDTH = 1600
MAX_IMAGE_HEIGHT = 1600
JPEG_QUALITY = 80


def _build_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


async def _update_file(file_id: str, **fields):
    await files_collection.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": fields},
    )


def _format_provider_error(exc: Exception) -> str:
    message = str(exc)
    if "rate limit" in message.lower() or "429" in message:
        return "Groq API rate limit reached. Wait a bit and retry the job."
    return f"Processing failed: {exc}"


def _encode_image_for_groq(image: Image.Image) -> str:
    prepared = image.copy()
    prepared.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT))

    buffer = BytesIO()
    prepared.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    prepared.close()
    return encoded


async def process_file(file_id: str, file_path: str):
    await _update_file(file_id, status="processing")
    print(f"Processing file with ID: {file_id}")

    pil_images = []

    try:
        pages = convert_from_path(file_path)

        for i, image in enumerate(pages):
            images_save_path = f"/mnt/uploads/images/{file_id}/image-{i}.jpg"
            os.makedirs(os.path.dirname(images_save_path), exist_ok=True)
            image.save(images_save_path, "JPEG")
            pil_images.append(Image.open(images_save_path))

        await _update_file(file_id, status="images_ready")

        client = _build_client()
        if client is None:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Configure it before processing files."
            )

        selected_images = pil_images[:MAX_IMAGES_PER_REQUEST]
        content = [
            {
                "type": "text",
                "text": (
                    "Based on the resume images below, roast this resume. "
                    "Be funny but not cruel. Mention strengths and weaknesses clearly."
                ),
            }
        ]

        for image in selected_images:
            encoded_image = _encode_image_for_groq(image)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    },
                }
            )

        if len(pil_images) > MAX_IMAGES_PER_REQUEST:
            content[0]["text"] += (
                f" Only the first {MAX_IMAGES_PER_REQUEST} pages are included because "
                "Groq vision requests support up to 5 images per request."
            )

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": "You are a witty but constructive resume reviewer.",
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
        )

        result_text = response.choices[0].message.content or "Groq returned an empty response."

        await _update_file(
            file_id,
            status="completed",
            result=result_text,
            error=None,
        )
        print(result_text)
    except Exception as exc:
        error_message = _format_provider_error(exc)
        await _update_file(
            file_id,
            status="failed",
            result=None,
            error=error_message,
        )
        print(error_message)
    finally:
        for image in pil_images:
            image.close()
