# Orbit Snake

Juego Snake de superheroes originales, desarrollado con Pygame y preparado
para ejecutarse en navegador mediante Pygbag.

## Héroes

Elige entre seis héroes originales, cada uno con el mismo rendimiento y una
identidad de color distinta: Nexo (azul), Solaria (amarillo), Brasa (rojo),
Fulgor (naranja), Gaia (verde) y Vesper (morado). La historia transcurre en
Nueva Aurora, una ciudad ficticia amenazada por drones que cruzan una grieta
de energía. Las apariencias, nombres y mundo son originales; no se usan
personajes, logotipos, imágenes ni música de terceros.

## Controles

- **Introducción:** Continuar / Enter / Espacio; omitir con el botón, Escape o S.
- **Menú:** Jugar / Enter para elegir héroe; I para instrucciones; C para créditos; Escape o Q para salir.
- **Elegir héroe:** pulsa `SELECCIONAR` en una de las seis tarjetas, usa 1–6 o las flechas; Enter comienza.
- **Moverse:** flechas o W, A, S y D.
- **En pantallas tactiles:** desliza el dedo dentro del tablero para cambiar de direccion; toca los botones para navegar.
- **Pausar / reanudar:** P o Escape.
- **Reiniciar la partida:** R.
- **Tras perder:** usa los botones, R, Enter o Espacio.

Recoge los núcleos de energía para sumar puntos y hacer crecer la serpiente. Evita chocar
contra los bordes o contra tu propio cuerpo. La pausa permite continuar,
reiniciar o volver al menú.

## Vidas y progresión

- La partida comienza con **1 vida** y permite guardar hasta **3**.
- Las recompensas de vida se desbloquean a los **5** y **15 puntos**. Se recogen
  al tocar el corazón rosa. Si ya tienes 3 vidas, la recompensa queda pendiente
  hasta que pierdas una vida.
- El nivel sube cada 3 puntos: empieza en 1, alcanza como máximo el 10 y aumenta
  la velocidad de 5 a 14 movimientos por segundo.
- La victoria se consigue al alcanzar **30 puntos en nivel 10** (objetivo
  configurable en `settings.py`) o al llenar el tablero. Derrota y victoria
  muestran pantallas independientes con opciones para repetir o volver al menú.
- A partir del nivel 3 aparecen obstáculos grises. La cantidad aumenta
  gradualmente hasta 10; permanecen en el tablero durante la partida.
- Una colisión pierde una vida. Si quedan vidas, la serpiente reaparece en una
  posición libre y recibe 1,5 segundos de protección.

## Requisitos

- Python 3.11 o una versión compatible con las dependencias.
- Google Chrome o un navegador moderno para la prueba web.

## Preparación en Windows

Desde esta carpeta, crea y activa un entorno virtual e instala las dependencias:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si no tienes Python 3.11, utiliza una versión de Python compatible con Pygame
Community Edition y Pygbag.

## Ejecución local

```powershell
python main.py
```

## Prueba en navegador

Desde la raíz del proyecto:

```powershell
pygbag .
```

Abre en Chrome la URL local que muestre Pygbag (normalmente
`http://localhost:8000`). Esta prueba local no publica el juego en Internet. El movimiento se actualiza
con un temporizador independiente de los fotogramas para conservar una
velocidad consistente.

## Ajuste de pantalla

Pygbag escala el lienzo manteniendo la proporcion 3:2 del juego y lo centra
cuando la ventana tiene otra proporcion. Se verifico en ventanas de 800 x 600,
360 x 800 y 1280 x 720. El lienzo conserva la proporcion, por lo que en
telefonos se recomienda jugar en horizontal. En pantallas tactiles se puede
deslizar dentro del tablero para dirigir la serpiente y tocar los botones para
navegar.

## Aviso conocido de Pygbag

Pygbag 0.9.3 puede mostrar `BrowserFS not found` porque su plantilla solicita
`browserfs.min.js` en la CDN y esa ruta devuelve HTTP 404. Se comprobo tambien
la URL oficial y el mismo recurso no esta disponible en las rutas revisadas.
El aviso no impide que esta partida arranque ni que sus controles funcionen en
Chrome. El origen esta en la plantilla/CDN de Pygbag, no en la logica del
juego; no se modifico el HTML generado ni se incorporo una copia local de una
dependencia externa. Conviene volver a revisarlo cuando Pygbag publique una
plantilla o recurso corregido.
