# Caso Recortado Studio en la nube (Railway)

Fase 1: publicar **la lista de espera** (sin IA ni vídeos). Fase 2: abrir la web con los vídeos hechos en Modal.

## Fase 1 · La lista de espera en Railway

1. **GitHub**: el código está en tu repositorio privado (`caso-recortado-studio`). No contiene tu voz, tus vídeos ni claves.
2. **Railway** (railway.com) → *Login with GitHub* → **New Project** → **Deploy from GitHub repo** → elige `caso-recortado-studio`.
   Railway ve el `Dockerfile` y lo construye solo (tarda unos 3-5 minutos la primera vez).
3. **Disco permanente**: en el servicio, **Settings → Volumes → Add volume** (o clic derecho → *Attach volume*),
   ruta de montaje **`/datos`**. Ahí se guardan la lista de espera, las cuentas y los vídeos: no se borra al actualizar.
4. **Variables** (pestaña *Variables* → *New variable*). Tus datos personales van SOLO aquí, nunca en el chat:

   | Variable | Valor |
   |---|---|
   | `CR_SOLO_LISTA` | `1` |
   | `CR_ADMIN_EMAIL` | tu email (con él entrarás a ver la lista) |
   | `CR_TITULAR` | tu nombre y apellidos |
   | `CR_NIF` | tu NIF |
   | `CR_DOMICILIO` | tu dirección |
   | `CR_EMAIL_CONTACTO` | el email de contacto que quieras mostrar |
   | `CR_ALOJAMIENTO` | `Railway Corp. (Estados Unidos)` |
   | `CR_URL` | la dirección del paso 5, con `https://` |

5. **Dirección web**: *Settings → Networking → Generate Domain*. Te da algo como `caso-recortado.up.railway.app`.
   Ponla en `CR_URL` y guarda (Railway reinicia solo).
6. **Tu cuenta de administrador**: abre `https://TU-DIRECCION/registro?admin=1` y crea la cuenta con el email de
   `CR_ADMIN_EMAIL`. En **Mi cuenta** verás cuántos se han apuntado y el botón **Descargar la lista (Excel)**.
7. Pon `https://TU-DIRECCION/lista-espera` en la bio de YouTube, Instagram y TikTok.

**Coste**: Railway da una prueba gratis y después un plan gratuito con poco crédito; esta web es pequeña, pero si se
queda corto, el plan Hobby cuesta unos 5 $/mes. Comprueba los precios en railway.com antes de pagar nada.

## Fase 2 · Abrir la web con vídeos (Modal)

Se añadirá aquí cuando montemos Modal: cuenta en modal.com, sus claves en las variables de Railway
(`MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`), la clave de Claude (`ANTHROPIC_API_KEY`) y quitar `CR_SOLO_LISTA`.
