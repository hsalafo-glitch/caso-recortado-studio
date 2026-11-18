"""Los 10 guiones del canal de GTA 6 (formato CLIP: voz en off sobre gameplay) para el lanzamiento (19-nov-2026).

Cada bloque: voz (lo que se dice), rotulo (texto fijo arriba), grabar (qué plano de juego poner debajo)
y encuadre («lleno» = recorte vertical con zoom; «marco» = plano horizontal entero, para menús y mapas).
Datos comprobados el 18-nov-2026: fuentes en canal_gta6/PLAN.md. La voz no describe nada del juego que no
haya contado Rockstar: así vale con cualquier clip.
"""

PRON = {"GTA": "ge te a", "PS5": "pe ese cinco", "Xbox": "Equisbox", "Series S": "Series ese",
        "Series X": "Series equis", "PC": "pe ce", "Online": "onlain", "Rockstar": "Rokstar",
        "Ultimate": "Áltimeit", "Vice City": "Vais Siti", "Jason": "Yéison", "Take-Two": "Teik Tu",
        "Grassrivers": "Grasrívers", "Gellhorn": "Guélhorn", "Miami": "Maiami", "FPS": "efe pe ese"}
PIE = "\n\nCanal no oficial, sin relación con Rockstar Games ni Take-Two. Datos comprobados el 18/11/2026."


def G(slug, gancho, titulo, alternativas, desc, bloques):
    return dict(slug=slug, gancho=gancho, titulo=titulo, alternativas=alternativas, descripcion=desc + PIE,
                pronuncia=PRON, marca="", bloques=[dict(voz=v, rotulo=r, grabar=g, encuadre=e) for v, r, g, e in bloques])


GUIONES = [
    # 01 · «cuando sale gta 6», «gta 6 release date» (+253 %) → publicar HOY antes de medianoche
    G("gta6-hora-salida", ["GTA 6", "¿A QUÉ HORA?"],
      "¿A qué hora sale GTA 6? Hora exacta en España y Latinoamérica",
      ["GTA 6 se desbloquea a MEDIANOCHE (hora por país)", "Hora de GTA 6 en tu país: no te equivoques"],
      "GTA 6 se desbloquea a medianoche, hora local de cada país. A qué hora juegas tú y qué hacer antes. "
      "#GTA6 #GTAVI #GTA6Lanzamiento #PS5 #Xbox", [
          ("GTA 6 ya está aquí. ¿Pero a qué hora exacta puedes jugar?", "¿A QUÉ HORA SALE?",
           "Pantalla de inicio o primer plano espectacular de la ciudad", "lleno"),
          ("Se desbloquea el 19 de noviembre a las doce de la noche, hora local de cada país.", "19 NOV · 00:00 LOCAL",
           "Reloj de la consola o menú de la tienda con el juego", "marco"),
          ("En España peninsular, a medianoche. En Canarias, una hora después. Y en México, siete horas más tarde que en Madrid.",
           "ESPAÑA · CANARIAS · MÉXICO", "Conducción por la ciudad de noche", "lleno"),
          ("Si lo compraste en digital, la precarga empezó el 10. Déjalo descargado y la consola en reposo para que se actualice.",
           "PRECARGA + REPOSO", "Barra de descarga o menú de la consola", "marco"),
          ("¿A qué hora empiezas tú? Te leo en comentarios.", "¿A QUÉ HORA JUEGAS?",
           "El mejor plano que tengas (cierre)", "lleno"),
      ]),
    # 02 · «gta 6 precio», «como comprar gta 6 barato»
    G("gta6-precio-ediciones", ["GTA 6", "¿CUÁNTO CUESTA?"],
      "Precio de GTA 6: Estándar vs Ultimate, ¿cuál comprar?",
      ["GTA 6 cuesta 79,99 €… ¿merece la Ultimate?", "No compres la edición equivocada de GTA 6"],
      "Lo que cuesta GTA 6 en España, qué trae cada edición y cuál te conviene. "
      "#GTA6 #GTA6Precio #GTAVI #PS5 #XboxSeries", [
          ("¿Cuánto cuesta de verdad GTA 6? Ojo, que hay dos ediciones.", "EL PRECIO DE GTA 6",
           "Plano de coches de lujo o dinero en el juego", "lleno"),
          ("En España, la estándar cuesta 79 euros con 99 en PlayStation 5 y Xbox Series. La Ultimate, 99 euros con 99.",
           "79,99 € · 99,99 €", "Tienda de la consola mostrando las ediciones", "marco"),
          ("Reservando antes del lanzamiento te llevabas un pack de regalo. Y la caja de tienda no trae disco: dentro hay un código.",
           "LA CAJA NO TRAE DISCO", "Gameplay libre: paseo por la playa", "lleno"),
          ("Mi consejo: empieza por la estándar. Si te engancha, pasas a la Ultimate después con una mejora aparte.",
           "EMPIEZA POR LA ESTÁNDAR", "Gameplay de acción: persecución o conducción", "lleno"),
          ("¿Cuál has comprado tú? ¿Estándar o Ultimate?", "¿CUÁL TIENES TÚ?", "Plano de cierre", "lleno"),
      ]),
    # 03 · «gta 6 tamaño», «como descargar gta 6 en ps5»
    G("gta6-cuanto-ocupa", ["GTA 6 OCUPA", "212 GB"],
      "¿Cuánto ocupa GTA 6? Haz hueco en PS5 y Xbox Series S",
      ["GTA 6 no te va a caber (si tienes Series S)", "212 GB: así haces sitio para GTA 6"],
      "GTA 6 pide hasta 212 GB. Cuánto espacio tiene tu consola y cómo hacer hueco. "
      "#GTA6 #GTAVI #PS5 #XboxSeriesS #GTA6Descarga", [
          ("Antes de jugar a GTA 6, mira tu espacio libre. Puede que no te quepa.", "¿TE CABE GTA 6?",
           "Pantalla de almacenamiento de la consola", "marco"),
          ("Rockstar pide hasta 212 gigas, según la consola. Y en algunas Xbox ya pasa de 230.", "HASTA 212 GB",
           "Plano aéreo o panorámico de la ciudad (que se vea lo grande que es)", "lleno"),
          ("Una PS5 normal tiene unos 667 gigas útiles. La Series S, unos 364: GTA 6 se come más de la mitad.",
           "SERIES S: MÁS DE LA MITAD", "Gameplay libre", "lleno"),
          ("Borra lo que no juegues, pasa juegos a un disco externo y deja activadas las actualizaciones automáticas.",
           "CÓMO HACER HUECO", "Menú de gestión de datos de la consola", "marco"),
          ("¿Cuánto espacio te queda a ti?", "¿CUÁNTO TE QUEDA?", "Plano de cierre", "lleno"),
      ]),
    # 04 · «gta 6 pc» (+381 %), «como jugar gta 6 en pc», «cuando sale gta 6 para pc»
    G("gta6-pc", ["GTA 6 EN PC", "¿CUÁNDO?"],
      "¿GTA 6 sale en PC? Lo que se sabe (y cuidado con las descargas)",
      ["GTA 6 en PC: la respuesta corta es NO (de momento)", "¿Cuándo llega GTA 6 a PC? Lo que pasó con GTA 5"],
      "GTA 6 llega solo a PS5 y Xbox Series. Qué pasó con GTA 5 en PC y por qué desconfiar de las descargas para PC. "
      "#GTA6 #GTA6PC #GTAVI #PCGaming #Rockstar", [
          ("¿Sale GTA 6 en PC? La respuesta corta es que, de momento, no.", "¿GTA 6 EN PC?",
           "Gameplay con buena calidad de imagen (detalle, luces)", "lleno"),
          ("Ha salido solo en PlayStation 5 y Xbox Series. Rockstar no ha dado ninguna fecha para ordenador.",
           "PC: SIN FECHA", "Conducción por la costa", "lleno"),
          ("Con GTA 5 pasó lo mismo. Salió en consolas en 2013 y no llegó a PC hasta 2015.", "GTA 5: 2013 → 2015",
           "Gameplay libre", "lleno"),
          ("Cuidado con las webs que prometen GTA 6 para PC ya. Son estafas o virus.", "¡OJO: ESTAFAS!",
           "Plano de tensión: policía, persecución", "lleno"),
          ("¿Esperas a la versión de PC o te pillas una consola?", "¿ESPERAS O CONSOLA?", "Plano de cierre", "lleno"),
      ]),
    # 05 · «como conseguir gta 6 gratis» (+87 %)
    G("gta6-gratis-estafa", ["GTA 6 GRATIS", "ES UNA TRAMPA"],
      "GTA 6 gratis: así es la estafa que está circulando",
      ["NO descargues GTA 6 gratis (mira esto)", "La trampa de GTA 6 gratis para móvil y PC"],
      "Descargas gratis, códigos regalados y versiones para móvil: cómo funcionan las estafas de GTA 6. "
      "#GTA6 #GTA6Gratis #Estafa #Ciberseguridad #GTAVI", [
          ("¿Has visto anuncios de GTA 6 gratis? Antes de pinchar, mira esto.", "¿GTA 6 GRATIS?",
           "Plano llamativo de gameplay", "lleno"),
          ("Cada gran lanzamiento trae lo mismo: descargas gratis, códigos regalados y versiones para móvil.",
           "LAS 3 TRAMPAS", "Gameplay libre", "lleno"),
          ("Te piden tu cuenta, tus datos o que instales un archivo. Y ese archivo te roba las contraseñas.",
           "ROBAN TU CUENTA", "Plano de robo o atraco en el juego", "lleno"),
          ("GTA 6 no tiene versión para móvil ni para PC, y nadie regala códigos por un comentario.",
           "NI MÓVIL NI PC", "Gameplay de acción", "lleno"),
          ("Compártelo con ese amigo que pincha en todo.", "¡COMPÁRTELO!", "Plano de cierre", "lleno"),
      ]),
    # 06 · «como comprar gta 6 en nueva zelanda», «como jugar gta 6 antes» (publicar HOY)
    G("gta6-truco-nueva-zelanda", ["12 HORAS ANTES", "¿FUNCIONA?"],
      "El truco de Nueva Zelanda para jugar GTA 6 antes: ¿funciona?",
      ["Jugar GTA 6 12 horas antes: el truco y su riesgo", "¿Cambiar de región para GTA 6? Ojo"],
      "GTA 6 se desbloquea a medianoche de cada país y Nueva Zelanda va 12 horas por delante de España. "
      "Qué riesgos tiene cambiar de región. #GTA6 #GTAVI #NuevaZelanda #PS5 #Xbox", [
          ("¿Se puede jugar a GTA 6 antes que nadie? Mucha gente busca el truco de Nueva Zelanda.",
           "¿JUGAR ANTES?", "Primeros minutos de gameplay", "lleno"),
          ("Como se desbloquea a medianoche de cada país, en Nueva Zelanda llega unas doce horas antes que en España.",
           "NZ: 12 HORAS ANTES", "Amanecer o atardecer en el juego", "lleno"),
          ("El truco es cambiar la región de la consola o de la cuenta a Nueva Zelanda.", "CAMBIAR DE REGIÓN",
           "Menú de ajustes de la consola", "marco"),
          ("Pero no siempre funciona: en PlayStation la compra va ligada a la región de tu cuenta, y puedes tener problemas con ella.",
           "RIESGO PARA TU CUENTA", "Plano de caos: choque o persecución", "lleno"),
          ("Yo esperaría a medianoche. ¿Tú lo intentarías?", "¿LO INTENTARÍAS?", "Plano de cierre", "lleno"),
      ]),
    # 07 · «que consola comprar para gta 6», «gta 6 ps5 pro» (+374 %), «gta 6 30 fps» (+1305 %), «series s»
    G("gta6-que-consola", ["¿QUÉ CONSOLA", "PARA GTA 6?"],
      "¿PS5, PS5 Pro o Series S para GTA 6? 30 FPS en todas",
      ["GTA 6 va a 30 FPS… también en PS5 Pro", "La mejor consola para GTA 6 (no es la que crees)"],
      "Rockstar confirma 30 FPS en todas las consolas, también en PS5 Pro. Qué cambia y cuál comprar. "
      "#GTA6 #PS5Pro #XboxSeriesS #GTA6FPS #GTAVI", [
          ("¿Qué consola es mejor para GTA 6? Te lo resumo rápido.", "¿QUÉ CONSOLA?",
           "Gameplay con mucho detalle gráfico", "lleno"),
          ("Rockstar ha confirmado 30 fotogramas por segundo en todas las consolas, también en la PS5 Pro.",
           "30 FPS EN TODAS", "Conducción rápida (se nota la fluidez)", "lleno"),
          ("La Pro gana en imagen: sombras con trazado de rayos y un reescalado más nítido. La Series S es la más barata, y la que peor se ve.",
           "CAMBIA LA IMAGEN", "Plano con reflejos, agua o luces de neón", "lleno"),
          ("Si ya tienes PS5 o Series X, no cambies. Si vas a comprar, la PS5 normal es la más equilibrada.",
           "YA TIENES: NO CAMBIES", "Gameplay libre", "lleno"),
          ("¿En qué consola juegas tú?", "¿EN CUÁL JUEGAS?", "Plano de cierre", "lleno"),
      ]),
    # 08 · «gta 6 map» / «gta 6 mapa» (ES 22 %), «gta 6 leonida», «gta 6 vice city»
    G("gta6-mapa-leonida", ["EL MAPA", "DE GTA 6"],
      "El mapa de GTA 6 explicado: las 6 zonas de Leonida",
      ["GTA 6 no es una ciudad: es un ESTADO entero", "Las 6 zonas del mapa de GTA 6"],
      "Leonida, el estado inspirado en Florida: Vice City, los Cayos, Grassrivers, Port Gellhorn, Ambrosia y el monte Kalaga. "
      "#GTA6 #GTA6Mapa #Leonida #ViceCity #GTAVI", [
          ("El mapa de GTA 6 no es una ciudad. Es un estado entero: Leonida, inspirado en Florida.", "LEONIDA = FLORIDA",
           "Mapa del juego abierto (alejado)", "marco"),
          ("Vice City, la gran ciudad inspirada en Miami. Y al sur, los Cayos de Leonida.", "VICE CITY · LOS CAYOS",
           "Vice City y después la costa o las islas", "lleno"),
          ("Grassrivers, pantanos con caimanes. Y Port Gellhorn, un puerto industrial.", "GRASSRIVERS · PORT GELLHORN",
           "Pantano y después puerto", "lleno"),
          ("Ambrosia, campo y fábricas. Y el monte Kalaga, un parque natural.", "AMBROSIA · MONTE KALAGA",
           "Campo y después montaña o bosque", "lleno"),
          ("¿Qué zona vas a explorar primero?", "¿QUÉ ZONA PRIMERO?", "El plano más bonito del mapa", "lleno"),
      ]),
    # 09 · «gta 6 lucia» (vol. 80, competencia 38), «jason gta 6»
    G("gta6-lucia-jason", ["LUCÍA Y JASON", "¿QUIÉNES SON?"],
      "Lucía y Jason: quiénes son los protagonistas de GTA 6",
      ["Por primera vez, una PAREJA protagoniza GTA", "Lucía Caminos y Jason Duval, explicados"],
      "Por primera vez, una pareja protagoniza un GTA. Lo que Rockstar ha contado de Lucía Caminos y Jason Duval. "
      "#GTA6 #Lucia #Jason #GTAVI #Leonida", [
          ("¿Quiénes son los protagonistas de GTA 6? Por primera vez, una pareja.", "LOS PROTAGONISTAS",
           "Los dos personajes juntos", "lleno"),
          ("Se llaman Lucía Caminos y Jason Duval, y juegas con los dos.", "LUCÍA CAMINOS · JASON DUVAL",
           "Lucía y después Jason", "lleno"),
          ("Lucía acaba de salir de la cárcel y quiere una vida mejor. Jason creció rodeado de timadores y siempre acaba metido en líos.",
           "UNA PAREJA CON PASADO", "Cada personaje por separado", "lleno"),
          ("Un golpe que parecía seguro se tuerce, y acaban en el lado más oscuro del lugar más soleado de Estados Unidos.",
           "UN GOLPE QUE SALE MAL", "Atraco o persecución con los dos", "lleno"),
          ("¿Con quién te quedas: Lucía o Jason?", "¿LUCÍA O JASON?", "Plano de cierre con los dos", "lleno"),
      ]),
    # 10 · «que pasara con gta 5 cuando sale gta 6»
    G("gta6-que-pasa-gta-online", ["¿SE ACABA", "GTA ONLINE?"],
      "¿Qué pasa con GTA 5 y GTA Online ahora que sale GTA 6?",
      ["GTA Online NO se apaga (lo confirma Take-Two)", "¿GTA 6 tiene online? La respuesta"],
      "GTA Online sigue: Take-Two confirma soporte después de GTA 6. GTA 6 sale sin modo online y aún sin fecha. "
      "#GTA6 #GTAOnline #GTA5 #GTAVI #Rockstar", [
          ("¿Qué pasa con GTA 5 y GTA Online ahora que ha salido GTA 6?", "¿SE ACABA GTA ONLINE?",
           "Gameplay de GTA 6", "lleno"),
          ("Tranquilo, no se apaga. Take-Two, la dueña de Rockstar, ha dicho que seguirá dando soporte a GTA Online.",
           "NO SE APAGA", "Gameplay libre", "lleno"),
          ("GTA 6 sale solo con modo historia. No tiene online el primer día, y aún no hay fecha.", "GTA 6: SOLO HISTORIA",
           "Escena de historia o misión", "lleno"),
          ("Los rumores apuntan a 2027, pero no hay nada confirmado. Tu personaje de GTA Online sigue ahí.",
           "RUMOR: 2027", "Gameplay de acción", "lleno"),
          ("¿Sigues en GTA Online o te pasas del todo a GTA 6?", "¿TE QUEDAS O TE PASAS?", "Plano de cierre", "lleno"),
      ]),
]


if __name__ == "__main__":
    for i, g in enumerate(GUIONES, 1):
        n = sum(len(b["voz"].split()) for b in g["bloques"])
        print(f"{i:02d} {g['slug']:28s} {n:3d} palabras  ≈{n * 0.39 + 2:4.1f} s")
