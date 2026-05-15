import json

from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.text import Truncator


SITE_NAME = "MasLove Notes"
SITE_TAGLINE = "Say What Your Heart's Been Holding."
SITE_DESCRIPTION = (
    "Write anonymous love notes, read heartfelt messages from Masbate, "
    "Philippines, and share each note through a QR code."
)
SITE_KEYWORDS = (
    "MasLove Notes, Masbate love notes, anonymous love notes, heartfelt "
    "messages, QR code notes, Masbate Philippines"
)


def clean_summary(value, length=155):
    text = " ".join(strip_tags(value or "").split())
    return Truncator(text).chars(length)


def build_schema(request):
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": SITE_NAME,
            "alternateName": "Maslove Notes",
            "url": request.build_absolute_uri("/"),
            "applicationCategory": "SocialNetworkingApplication",
            "operatingSystem": "Web",
            "description": SITE_DESCRIPTION,
            "areaServed": {
                "@type": "Place",
                "name": "Masbate, Philippines",
            },
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "PHP",
            },
        },
        separators=(",", ":"),
    )


def build_seo(
    request,
    *,
    title=None,
    description=None,
    canonical_path=None,
    image_path="assets/og-image.png",
    page_type="website",
    robots="index,follow",
):
    return {
        "title": title or f"{SITE_NAME} | Anonymous Love Notes in Masbate, Philippines",
        "description": clean_summary(description or SITE_DESCRIPTION),
        "keywords": SITE_KEYWORDS,
        "canonical_url": request.build_absolute_uri(canonical_path or request.path),
        "image_url": request.build_absolute_uri(static(image_path)),
        "type": page_type,
        "robots": robots,
        "schema": build_schema(request),
    }
