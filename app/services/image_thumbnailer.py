# app/services/image_thumbnailer.py
import hashlib
import io
import re
from typing import Optional, Tuple

import httpx
from PIL import Image

from app.utils.supabase_client import supabase


class ImageThumbnailer:
    """
    Télécharge une image (URL publique Supabase), crée un thumbnail (JPEG),
    l'upload dans un bucket cache, et renvoie l'URL publique du thumbnail.
    """

    DEFAULT_BUCKET = "user-photos-cache"
    DEFAULT_MAX_SIDE = 768  # 512–768 recommandé pour vision stable + coût bas
    DEFAULT_QUALITY = 85

    @staticmethod
    def _hash_key(s: str) -> str:
        return hashlib.sha256((s or "").encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def _parse_supabase_object_path(public_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Ex: https://xxx.supabase.co/storage/v1/object/public/user-photos/<userId>/face_xxx.jpg
        -> bucket="user-photos", path="<userId>/face_xxx.jpg"
        """
        if not public_url:
            return None, None

        m = re.search(r"/storage/v1/object/public/([^/]+)/(.+)$", public_url)
        if not m:
            return None, None
        return m.group(1), m.group(2)

    @classmethod
    def _ensure_bucket_exists(cls, bucket_name: str) -> None:
        """
        Vérifie que le bucket existe, de façon compatible supabase-py (retour variable selon versions).
        Ne tente pas de créer (tu l’as déjà créé dans l’UI).
        """
        try:
            client = supabase.get_client()
            existing = client.storage.list_buckets()

            # supabase-py peut renvoyer: {"data":[...]} ou un objet avec .data, ou directement une liste
            if isinstance(existing, dict):
                buckets = existing.get("data") or existing.get("buckets") or []
            else:
                buckets = getattr(existing, "data", None)
                if buckets is None:
                    buckets = existing if isinstance(existing, list) else []

            names = []
            for b in buckets or []:
                if isinstance(b, dict):
                    names.append(b.get("name"))
                else:
                    names.append(getattr(b, "name", None))

            names = [n for n in names if n]

            if bucket_name not in names:
                print(f"⚠️ Bucket '{bucket_name}' non trouvé dans list_buckets(). Noms vus={names[:20]}")
        except Exception as e:
            print(f"⚠️ Impossible de lister les buckets: {e}")


    @classmethod
    async def get_or_create_thumbnail_url(
        cls,
        source_url: str,
        bucket_name: Optional[str] = None,
        max_side: int = DEFAULT_MAX_SIDE,
        quality: int = DEFAULT_QUALITY,
    ) -> str:
        """
        Retourne l'URL publique du thumbnail.
        Si le thumbnail existe déjà dans le bucket cache, on le renvoie directement.
        """
        if not source_url:
            return source_url

        bucket = (bucket_name or cls.DEFAULT_BUCKET).strip()
        cls._ensure_bucket_exists(bucket)

        # clé stable basée sur l'URL source (et donc sur la photo)
        key = cls._hash_key(source_url)
        thumb_path = f"thumbnails/face_{key}_{max_side}.jpg"

        client = supabase.get_client()

        # 1) Si déjà uploadé, renvoyer l'URL publique
        try:
            # supabase-py: get_public_url retourne souvent {"publicUrl": "..."} ou direct str selon version
            public = client.storage.from_(bucket).get_public_url(thumb_path)
            public_url = public.get("publicUrl") if isinstance(public, dict) else str(public or "")
            if public_url:
                # test existence en HTTP GET 
                async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as h:
                    r = await h.get(public_url, headers={"Range": "bytes=0-0"})
                    if r.status_code in (200, 206):
                        return public_url

        except Exception:
            pass

        # 2) Télécharger l'image source
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as http:
            resp = await http.get(source_url)
            resp.raise_for_status()
            img_bytes = resp.content

        # 3) Resize via Pillow
        im = Image.open(io.BytesIO(img_bytes))
        im = im.convert("RGB")  # JPEG
        w, h = im.size
        largest = max(w, h)
        if largest > max_side:
            scale = max_side / float(largest)
            new_w = int(w * scale)
            new_h = int(h * scale)
            im = im.resize((new_w, new_h), Image.LANCZOS)

        out = io.BytesIO()
        im.save(out, format="JPEG", quality=int(quality), optimize=True)
        out.seek(0)

        # 4) Upload dans bucket cache
        try:
            file_options = {"content-type": "image/jpeg", "upsert": "true"}
            client.storage.from_(bucket).upload(thumb_path, out.getvalue(), file_options=file_options)
        except TypeError:
            # compat supabase-py versions (parfois "options" au lieu de file_options)
            client.storage.from_(bucket).upload(thumb_path, out.getvalue(), {"content-type": "image/jpeg", "upsert": "true"})
        except Exception as e:
            print(f"❌ Upload thumbnail échoué: {e}")
            print("   ↳ Cause probable: clé Supabase sans droits d'écriture Storage (anon key). Utiliser service role côté backend.")
            return source_url


        # 5) URL publique
        public = client.storage.from_(bucket).get_public_url(thumb_path)
        public_url = public.get("publicUrl") if isinstance(public, dict) else str(public or "")
        return public_url or source_url
