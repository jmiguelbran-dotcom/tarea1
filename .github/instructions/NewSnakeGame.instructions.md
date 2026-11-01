# Orbit Snake: Guardianes de Nueva Aurora

## Propósito del documento

Estas instrucciones describen la versión actual del videojuego Orbit Snake para
que el código, la interfaz y la documentación mantengan los mismos requisitos.
Es un proyecto de prueba y documentación, no un producto publicado.

## Concepto y alcance

Orbit Snake es un juego arcade de Snake con una historia original de ciencia
ficción y superhéroes. Seis héroes protegen la ciudad ficticia de Nueva Aurora
de drones que llegan por una grieta de energía. El jugador reúne núcleos de
energía naranjas, crece y sobrevive a una dificultad progresiva.

Los nombres, héroes, ciudad, historia y elementos visuales del juego son
originales. No incorporar personajes, nombres, logotipos, ilustraciones,
diálogos ni música de franquicias existentes. Los héroes son apariencias: no
otorgan ventajas distintas de velocidad o capacidad.

## Tecnología y ejecución

- Python compatible con pygame-ce y Pygbag.
- pygame-ce para el juego y sus gráficos geométricos.
- Pygbag para ejecutar el proyecto en navegadores mediante WebAssembly.
- Bucle principal asíncrono; no usar `time.sleep()` ni otras esperas bloqueantes.
- Mantener recursos locales y rutas relativas. El juego debe funcionar sin
  archivos gráficos o de audio externos.
- Resolución lógica de 960 × 640, con tablero de 36 × 19 casillas de 24 px.
- FPS de renderizado: 60. La velocidad de movimiento se calcula con un
  acumulador de tiempo y no depende de los FPS.

Instalación en Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Ejecución local y prueba en navegador:

```powershell
python main.py
pygbag .
```

Abrir la dirección local indicada por Pygbag (normalmente
`http://localhost:8000`). Ejecutar en localhost no publica el juego.

## Héroes seleccionables

El selector contiene seis héroes originales. Cada color identifica su estilo
visual y no cambia las reglas de juego:

| Héroe | Color principal |
|---|---|
| Nexo | Azul |
| Solaria | Amarillo |
| Brasa | Rojo |
| Fulgor | Naranja |
| Gaia | Verde |
| Vesper | Morado |

Cada tarjeta debe mostrar nombre, breve descripción, representación geométrica
y botón `SELECCIONAR`. El seleccionado se destaca con su color de acento. La
cabeza y el cuerpo de la serpiente mantienen ese estilo.

## Historia e interfaz

La introducción contiene tres bloques narrativos:

1. Una grieta luminosa aparece sobre Nueva Aurora y libera drones.
2. Seis héroes originales unen sus talentos para proteger la ciudad.
3. El jugador reúne núcleos, evita obstáculos y ayuda al equipo a resistir.

La introducción se puede omitir. El menú ofrece Jugar, Cómo jugar, Créditos y
Salir. La selección de héroe conduce a la partida; durante el juego se muestran
héroe, puntos, nivel, velocidad, vidas, longitud y pausa. También hay pantallas
de pausa, derrota y victoria.

Los gráficos se dibujan con formas de Pygame. El fondo representa una ciudad
ficticia bajo una grieta de energía. Los núcleos naranjas son la comida, los
corazones rosas son recompensas de vida y los obstáculos son grises.

## Reglas de juego

### Movimiento y controles

- La serpiente empieza con tres segmentos y se mueve continuamente por casillas.
- Flechas o W/A/S/D cambian la dirección; no se permite girar 180 grados.
- En pantallas táctiles, deslizar dentro del tablero cambia la dirección; tocar
  brevemente activa los botones.
- P o Escape pausa y reanuda. R reinicia durante la partida. Los botones de las
  pantallas también permiten continuar, reiniciar y volver al menú.

### Núcleos, puntuación y crecimiento

- La partida comienza con un núcleo en una casilla libre.
- Al recogerlo, suma 1 punto, añade un segmento y genera otro núcleo en un lugar
  que no esté ocupado por la serpiente, obstáculos o recompensa de vida.
- Si no quedan casillas libres para comida, la partida se gana.

### Niveles y velocidad

El nivel empieza en 1, sube cada tres puntos hasta el nivel 10 y determina los
movimientos por segundo:

| Nivel | Puntos mínimos | Movimientos/segundo |
|---:|---:|---:|
| 1 | 0 | 5 |
| 2 | 3 | 6 |
| 3 | 6 | 7 |
| 4 | 9 | 8 |
| 5 | 12 | 9 |
| 6 | 15 | 10 |
| 7 | 18 | 11 |
| 8 | 21 | 12 |
| 9 | 24 | 13 |
| 10 | 27 | 14 |

La velocidad no debe superar 14 movimientos por segundo ni el nivel debe
superar 10. La derrota conserva el puntaje y nivel de la partida; al reaparecer
no se reinicia la progresión.

### Obstáculos

Los obstáculos grises se agregan progresivamente cuando la partida alcanza un
nivel nuevo. La cantidad objetivo por nivel es 0, 0, 2, 3, 4, 5, 6, 7, 8 y 10.
Se mantienen hasta reiniciar la partida y no aparecen sobre la serpiente, la
comida o una recompensa de vida.

### Vidas, colisiones y protección

- La partida inicia con 1 vida; el máximo es 3.
- Una colisión con borde, cuerpo u obstáculo resta una vida.
- Si quedan vidas, la serpiente reaparece en una ubicación libre con 1,5
  segundos de protección. Se conservan puntos, nivel y obstáculos.
- La posición de reaparición y su siguiente casilla deben quedar dentro del
  tablero y libres de obstáculos, objetos y segmentos de la serpiente.
- Al perder la última vida se muestra la pantalla de derrota.

### Recompensas de vida

- Se desbloquea una recompensa en 5 puntos y otra en 15.
- Se representa como un corazón rosa.
- Con menos de 3 vidas, aparece en una casilla libre. Si el jugador ya tiene 3
  vidas, la recompensa permanece pendiente hasta que pierda una vida.
- Recogerla aumenta las vidas en 1, sin exceder el máximo de 3.

### Victoria

Se gana al alcanzar 30 puntos en nivel 10 o al llenar el tablero. El objetivo
configurable está en `settings.py`. La pantalla final ofrece volver a jugar o al
menú.

## Estructura actual

```text
main.py                         bucle asíncrono, estados, controles y render
settings.py                     pantalla, tablero, colores y progresión
game/characters.py              seis héroes y sus paletas originales
game/game_manager.py            estado de partida, puntuación, vidas y victoria
game/snake.py                   segmentos, giros, movimiento y colisiones
game/obstacles.py               colocación progresiva de obstáculos
game/powerups.py                recompensas de vida pendientes
game/screens.py                 introducción, menús, selector y pantallas finales
tests/test_game_logic.py        pruebas de lógica, pantallas y controles táctiles
README.md                       instalación, controles y guía para probar
```

Mantener la lógica separada de la representación. Validar todas las posiciones
generadas y no añadir dependencias incompatibles con Pygbag sin probarlas.

## Validación de cambios

Antes de dar por terminado un cambio:

1. Ejecutar `python -m unittest discover -s tests -v`.
2. Ejecutar `python -m compileall -q main.py game settings.py tests`.
3. Ejecutar `git diff --check`.
4. Para cambios de interfaz o controles, probar el recorrido correspondiente
   en Chrome mediante `pygbag .`.
5. Confirmar que los seis nombres y colores se mantienen sincronizados entre
   código, selector, pruebas y documentación.

Este repositorio es para pruebas y documentación. La publicación externa no es
un requisito del proyecto.
