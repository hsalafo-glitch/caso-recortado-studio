# Canal de GTA 6: plan de lanzamiento (19 de noviembre de 2026)

## Cómo se hace un vídeo (cuando tengas los clips)

1. Graba tu partida (en PS5: botón Crear → «Guardar clip»; en Xbox: botón Compartir) y pasa los clips al ordenador.
2. Mete los clips en `canal_gta6/clips/` (sirven para todos los vídeos) o en `canal_gta6/clips/01/`, `02/`…
   si quieres clips concretos para un vídeo. En el archivo `salida/gta6/<vídeo>.txt` pone qué plano conviene
   para cada parte.
3. Ejecuta:

   ```bash
   python canal_gta6/fabrica_clips.py 01        # o «todos»
   ```

   La voz ya está hecha (está en `cache_audio/`), así que cada vídeo tarda menos de un minuto.
4. Sube `salida/gta6/<vídeo>.mp4` y copia el título y la descripción de `salida/gta6/<vídeo>.txt`.

Para revisar el ritmo sin clips: `python canal_gta6/fabrica_clips.py 01 --demo` (fondo de prueba con la
lista de planos).

## Derechos (importante para no perder el canal)

- Usa solo **tu propio gameplay** o clips de creadores que te hayan dado permiso (algunos streamers tienen
  programas de clippers). Que un streamer juegue legalmente no te da permiso para resubir su directo: el
  vídeo es suyo y puede reclamarlo, igual que Rockstar.
- Nada de material filtrado ni de antes del lanzamiento.
- Nombre, logo y miniaturas tienen que ser tuyos: no uses el logo de GTA ni el arte oficial como marca del
  canal. En las descripciones ya va «Canal no oficial».

## Orden de publicación (de más urgente a menos)

| # | Vídeo | Búsqueda que ataca (vidIQ, 18-nov) | Cuándo |
|---|---|---|---|
| 01 | ¿A qué hora sale GTA 6? | «cuando sale gta 6», «gta 6 release date» (+253 %) | Hoy, antes de medianoche |
| 06 | Truco de Nueva Zelanda | «como comprar gta 6 en nueva zelanda», «como jugar gta 6 antes» | Hoy |
| 03 | ¿Cuánto ocupa? | «como descargar gta 6 en ps5» | Hoy / día 19 |
| 02 | Precio y ediciones | «como comprar gta 6 barato» | Día 19 |
| 07 | ¿Qué consola? | «gta 6 30 fps» (+1305 %), «gta 6 ps5 pro» (+374 %), «series s» | Día 19 |
| 04 | ¿Sale en PC? | «gta 6 pc» (+381 %), «como jugar gta 6 en pc» | Día 19-20 |
| 05 | GTA 6 gratis = estafa | «como conseguir gta 6 gratis» (+87 %) | Día 20 |
| 08 | Mapa de Leonida | «gta 6 mapa» (22 % de las búsquedas desde España), «gta 6 map» | Día 20-21 |
| 09 | Lucía y Jason | «gta 6 lucia» (volumen 80, competencia baja: 38) | Día 21 |
| 10 | ¿Qué pasa con GTA Online? | «que pasara con gta 5 cuando sale gta 6» | Día 22 |

Después del lanzamiento, lo que más se buscará es lo que solo se sabe jugando: «cómo ganar dinero en GTA 6»
(en las búsquedas de preguntas ya sale con volumen 68), secretos, primeras misiones y trucos. Graba eso
mientras juegas y yo te escribo los guiones sobre lo que hayas grabado.

## Datos usados y fuentes (comprobados el 18-nov-2026)

- Sale el 19-nov-2026 a medianoche hora local, PS5 y Xbox Series; precarga desde el 10-nov; sin fecha para PC;
  sin modo online el día uno.
  [Yahoo Tech](https://tech.yahoo.com/gaming/breaking-news/article/gta-6-launches-this-week-pre-loads-global-release-pricing-and-everything-else-you-need-to-know-about-the-highly-anticipated-game-160715994.html),
  [PBS](https://www.pbs.org/newshour/arts/the-long-wait-is-almost-over-heres-what-to-know-about-the-upcoming-release-of-grand-theft-auto-vi),
  [Forbes](https://www.forbes.com/sites/erikkain/2026/11/16/gta-6-release-date-time-ps5-xbox-series-x-download-size-day-one-update/)
- España: 79,99 € estándar y 99,99 € Ultimate; 00:00 en la península, Canarias una hora después; la caja trae un código.
  [eldiario.es](https://www.eldiario.es/spin/comprar-gta-6-espana-guia-tiendas-precios-oficiales-ediciones-extras-reservar-pm_1_13668447.html),
  [SomosXbox](https://www.somosxbox.com/gta-6-en-xbox-fecha-hora-en-espana-tamano-precio-y-ediciones/),
  [noobs.es](https://noobs.es/guia/gta-6-fecha-de-lanzamiento-plataformas-precio-y-ediciones/)
- Hasta 212 GB (algunas Xbox, 234 GB).
  [PCWorld](https://www.pcworld.com/article/3276995/gta-6-pre-load-starts-next-week-heres-what-to-do-before-then.html),
  [GamingBible](https://www.gamingbible.com/news/gta-6-release-time-preload-download-size-editions-385283-20261012)
- 30 FPS en todas las consolas, también en PS5 Pro (la Pro: sombras con trazado de rayos y PSSR).
  [Notebookcheck](https://www.notebookcheck.net/Rockstar-reveals-GTA-6-console-performance-targets-and-PS5-Pro-upgrades.1447121.0.html),
  [G2A News](https://www.g2a.com/news/gta-6-news/will-gta-6-run-at-60-fps/)
- Las 6 zonas de Leonida, y sin tamaño oficial del mapa.
  [Gfinity](https://www.gfinityesports.com/article/gta-6-map-guide-every-confirmed-location-in-leonida),
  [Beebom](https://beebom.com/gta-6-map)
- GTA Online seguirá con soporte (Take-Two); el online de GTA 6 no tiene fecha (los rumores dicen 2027).
  [Operation Sports](https://www.operationsports.com/gta-6-is-coming-in-november-but-rockstar-isnt-leaving-the-current-gta-online-behind/),
  [RockstarINTEL](https://rockstarintel.com/gta-online-support-will-continue-even-after-gta-6-releases-confirms-take-two/)
- Lucía y Jason: textos de presentación de Rockstar (Lucía sale de la cárcel; Jason creció entre timadores; «el
  lado más oscuro del lugar más soleado de Estados Unidos»).

## Voz

Kokoro (`em_alex`, modelo abierto Apache 2.0) porque ElevenLabs tiene la cuenta gratuita bloqueada y vidIQ solo
tenía 85 créditos. Escúchala antes de publicar. Para cambiar de voz: `VOZ_KOKORO=ef_dora` (mujer) o
`VOZ_KOKORO_VELOCIDAD=1.15` (más rápida), borra `cache_audio/<vídeo>/texto.txt` y vuelve a ejecutar.
