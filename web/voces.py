"""Voces que pueden elegir los clientes de la web. Todas están diseñadas por descripción con Qwen3-TTS VoiceDesign:
no copian a ninguna persona real. La voz del dueño del canal («usuario…») NUNCA se ofrece aquí."""
VOCES = {
    "narrador":  "Narrador grave",
    "cercano":   "Chico cercano",
    "narradora": "Narradora",
    "cercana":   "Chica cercana",
}
POR_DEFECTO = "narrador"


def valida(v):
    return v if v in VOCES else POR_DEFECTO
