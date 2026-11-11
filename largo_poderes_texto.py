"""Narración del vídeo largo «¿Qué pasaría si los superpoderes se consiguieran con experimentos?»"""

BLOQUES_VOZ = [
    # 1 gancho
    "¿Qué pasaría si los superpoderes fueran reales… pero la única forma de conseguirlos fuera presentarte "
    "voluntario a un experimento? Algunos salen increíblemente bien. Otros… salen muy, muy mal. Imagina que mañana "
    "abre el primer laboratorio de poderes del mundo. Y que tú estás en la cola.",
    # 2 reglas
    "Primero, las reglas de este mundo. Nadie nace con poderes. Todo sale de un laboratorio: genes editados, "
    "implantes y fármacos experimentales. Cada voluntario firma un contrato de cuarenta páginas, y en la última hay "
    "una frase en letra pequeña: el laboratorio no garantiza el resultado. Esa frase va a ser importante.",
    # 3 superfuerza
    "Experimento número uno: superfuerza. Y aquí la ciencia ya tiene una pista real. Existe un gen, el de la "
    "miostatina, que funciona como un freno para los músculos. Hay razas de vacas en las que ese freno no funciona, "
    "y son auténticas montañas de músculo. Incluso se han documentado personas con esa mutación, mucho más fuertes "
    "de lo normal desde niños. Así que el laboratorio quita el freno. Y funciona. El sujeto uno levanta una moto "
    "como si fuera una bolsa de la compra. Pero el músculo cuesta energía: ahora necesita comer más de seis mil "
    "calorías al día. Si se salta una comida, su propio cuerpo empieza a consumir esos músculos. Superfuerza, sí… "
    "y hambre para siempre.",
    # 4 visión nocturna
    "Experimento número dos: visión nocturna. También tiene una base real. En el año dos mil quince, un grupo de "
    "biohackers se echó en los ojos unas gotas con un compuesto parecido al que usan algunos peces de las "
    "profundidades, y aseguraron ver siluetas en la oscuridad a más de cincuenta metros. Nunca se demostró de forma "
    "científica, pero en nuestro mundo el laboratorio lo perfecciona. Resultado: un éxito total. La sujeto dos ve de "
    "noche como si fuera de día. Su único problema es que el sol del mediodía le resulta insoportable, así que vive "
    "con gafas de sol. Probablemente, es el mejor poder de esta lista.",
    # 5 invisibilidad
    "Experimento número tres: invisibilidad. Y aquí empieza lo malo. El laboratorio consigue que la luz atraviese "
    "todo el cuerpo del sujeto tres, como si fuera de cristal. Desaparece delante de todos. Aplausos. Hasta que "
    "alguien pregunta lo obvio: para ver, tus ojos necesitan atrapar la luz. Si la luz te atraviesa, no se queda en "
    "tu retina. El sujeto tres es perfectamente invisible… y completamente ciego. Nadie puede verle, y él no puede "
    "ver a nadie.",
    # 6 regeneración
    "Experimento número cuatro: regeneración. La inspiración es el ajolote, un animal real de México capaz de "
    "regenerar sus patas, su cola e incluso partes de su corazón y de su cerebro. El laboratorio copia ese truco en "
    "una persona. Al principio, es un milagro: un corte se cierra en minutos y un hueso roto se suelda en una "
    "noche. Pero regenerar significa que las células se dividen una y otra vez. Y cuando las células se dividen sin "
    "control, eso tiene otro nombre: tumor. Al sujeto cuatro se le cura una herida… y le aparece un bulto. El poder "
    "funciona demasiado bien.",
    # 7 telepatía
    "Experimento número cinco: telepatía. Hoy ya existen implantes cerebrales reales que permiten a personas "
    "paralizadas mover un cursor o escribir solo con el pensamiento. El laboratorio va un paso más allá: un implante "
    "que conecta dos cerebros. El sujeto cinco puede escuchar lo que piensa la persona de al lado. Funciona "
    "perfecto… en una habitación vacía. En la calle oye a cientos de personas a la vez: prisas, enfados, secretos "
    "que nunca quiso saber. A los tres días, pide una sola cosa: un botón para apagarlo.",
    # 8 volar
    "Experimento número seis: volar. Para levantar a una persona del suelo harían falta unas alas enormes y un "
    "cuerpo mucho más ligero. Así que el laboratorio hace lo que hacen las aves: vacía los huesos por dentro. Y el "
    "sujeto seis vuela. Durante unos segundos, es lo más bonito que ha visto nadie. Pero unos huesos huecos son "
    "unos huesos frágiles. Un mal aterrizaje, una caída tonta… y se rompe. Puede volar, pero no puede tropezar.",
    # 9 teletransporte
    "Y el experimento número siete, el que nadie quería probar: teletransporte. La máquina escanea tu cuerpo átomo "
    "a átomo, lo desmonta aquí… y lo vuelve a construir al otro lado de la sala. El sujeto siete entra, desaparece "
    "y aparece a diez metros, sonriendo. Dice que se siente igual. Recuerda su infancia, su nombre, todo. Pero los "
    "científicos se miran en silencio. Porque la máquina no le ha movido: ha destruido al original y ha construido "
    "una copia perfecta. Entonces… ¿quién ha salido de la máquina?",
    # 10 sociedad
    "Ahora piensa en un mundo lleno de estos laboratorios. ¿Quién podría pagar el primer poder? Probablemente, los "
    "más ricos. Los gobiernos querrían soldados con superfuerza. Las aseguradoras subirían el precio a quien se "
    "regenera. Aparecerían laboratorios ilegales, más baratos… y mucho más peligrosos. Y habría que registrar a "
    "cada persona con poderes, igual que hoy registramos un coche.",
    # 11 final
    "Al final, los poderes se parecerían mucho a la ciencia de verdad: cada avance tiene un precio, y casi nunca se "
    "ve en la primera prueba. Así que te pregunto: sabiendo que puede salir muy bien… o muy mal, ¿te apuntarías? ¿Y "
    "qué poder elegirías? Te leo en los comentarios.",
]

if __name__ == "__main__":
    t = "\n\n".join(BLOQUES_VOZ)
    print(len(t.split()), "palabras,", len(t), "caracteres")
