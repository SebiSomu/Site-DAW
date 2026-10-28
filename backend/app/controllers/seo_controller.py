from xml.sax.saxutils import escape

from flask import Blueprint, Response, request

from app.services.catalog_service import CatalogService

seo_bp = Blueprint("seo", __name__)

PRIVATE_PATHS = ("/account", "/admin", "/checkout")


@seo_bp.get("/robots.txt")
def robots():
    lines = ["User-agent: *", "Allow: /", *(f"Disallow: {path}" for path in PRIVATE_PATHS)]
    lines.append(f"Sitemap: {request.url_root}sitemap.xml")
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


@seo_bp.get("/sitemap.xml")
def sitemap():
    base_url = request.url_root.rstrip("/")
    entries = "".join(f"<url><loc>{escape(base_url + path)}</loc></url>" for path in CatalogService().public_paths())
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>'
    )
    return Response(body, mimetype="application/xml")
