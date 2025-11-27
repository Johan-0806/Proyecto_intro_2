import pygame
import random
import sys
import os
import math
import time
from PIL import Image, ImageSequence

##########################################
# INICIALIZACIÓN DE PYGAME Y CONFIGURACIÓN
##########################################
pygame.init()
info = pygame.display.Info()
ANCHO = info.current_w
ALTO = info.current_h
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Escapa del Laberinto")
reloj = pygame.time.Clock()

##########################################
# DEFINICIÓN DE COLORES
##########################################
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
GRIS = (100, 100, 100)
VERDE_OSCURO = (0, 100, 0)
AZUL_CLARO = (100, 100, 255)
GRIS_OSCURO = (50, 50, 50)
AZUL_HOVER = (0, 100, 255)
VERDE_CLARO = (100, 255, 100)
AMARILLO = (255, 255, 0)
NARANJA = (255, 165, 0)
MORADO = (128, 0, 128)
ROJO_OSCURO = (139, 0, 0)

##########################################
# CARGA DE RECURSOS GRÁFICOS
##########################################
try:
    # Carga de imágenes principales
    if os.path.exists("pared.png"):
        imagen_muro = pygame.image.load("pared.png")
    elif os.path.exists("assets/pared.png"):
        imagen_muro = pygame.image.load("assets/pared.png")
    else:
        raise FileNotFoundError("No se encontró pared.png")
    
    if os.path.exists("piedra.png"):
        imagen_suelo = pygame.image.load("piedra.png")
    elif os.path.exists("assets/piedra.png"):
        imagen_suelo = pygame.image.load("assets/piedra.png")
    else:
        raise FileNotFoundError("No se encontró piedra.png")
    
    if os.path.exists("prota_cat.png"):
        imagen_jugador = pygame.image.load("prota_cat.png")
    elif os.path.exists("assets/prota_cat.png"):
        imagen_jugador = pygame.image.load("assets/prota_cat.png")
    else:
        raise FileNotFoundError("No se encontró prota_cat.png")
    
    if os.path.exists("caza_cat.png"):
        imagen_cazador = pygame.image.load("caza_cat.png")
    elif os.path.exists("assets/caza_cat.png"):
        imagen_cazador = pygame.image.load("assets/caza_cat.png")
    else:
        raise FileNotFoundError("No se encontró caza_cat.png")
    
    # Carga de imagen de mina
    if os.path.exists("mina.png"):
        imagen_mina_original = pygame.image.load("mina.png")
    elif os.path.exists("assets/mina.png"):
        imagen_mina_original = pygame.image.load("assets/mina.png")
    else:
        imagen_mina_original = None
    
    # Carga de animación de explosión
    imagenes_explosion = []
    try:
        gif_path = "explosion.gif"
        assets_gif_path = "assets/explosion.gif"
        
        if os.path.exists(gif_path):
            gif = Image.open(gif_path)
        elif os.path.exists(assets_gif_path):
            gif = Image.open(assets_gif_path)
        else:
            raise FileNotFoundError("No se encontró explosion.gif")
        
        for frame in ImageSequence.Iterator(gif):
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            frame_data = frame.tobytes()
            frame_size = frame.size
            pygame_frame = pygame.image.fromstring(frame_data, frame_size, 'RGBA')
            imagenes_explosion.append(pygame_frame)
        usar_gif = True
        
    except:
        usar_gif = False
    
    # Crear explosión procedural si no hay GIF
    if not usar_gif or not imagenes_explosion:
        imagenes_explosion = []
        for i in range(8):
            tamaño = 30 + i * 15
            surface = pygame.Surface((tamaño, tamaño), pygame.SRCALPHA)
            if i < 4:
                color = (255, 165 - i*10, 0, 220 - i*30)
            else:
                color = (200 - (i-4)*30, 60 - (i-4)*15, 0, 150 - (i-4)*25)
            pygame.draw.circle(surface, color, (tamaño//2, tamaño//2), tamaño//2)
            for _ in range(5):
                px = random.randint(0, tamaño-1)
                py = random.randint(0, tamaño-1)
                radio_part = random.randint(2, 5)
                pygame.draw.circle(surface, (255, 255, 200, 150), (px, py), radio_part)
            imagenes_explosion.append(surface)
    
    # Verificar carga correcta de imágenes
    if imagen_muro and imagen_suelo and imagen_jugador and imagen_cazador:
        usar_imagenes = True
    else:
        raise Exception("Una o más imágenes principales no se cargaron correctamente")
        
except Exception as e:
    usar_imagenes = False
    imagen_jugador = None
    imagen_cazador = None
    imagen_mina_original = None
    imagenes_explosion = []

##########################################
# ESTADOS DEL JUEGO Y VARIABLES GLOBALES
##########################################
MENU_PRINCIPAL = 0
MODO_ESCAPA = 1
MODO_CAZADOR = 2
REGISTRO = 3
PUNTUACIONES = 4

estado_actual = MENU_PRINCIPAL
nombre_jugador = ""
puntuaciones_escapar = []  # Almacena top 5 modo escapar
puntuaciones_cazador = []  # Almacena top 5 modo cazador

##########################################
# CONFIGURACIÓN DE FUENTES DE TEXTO
##########################################
try:
    fuente_titulo = pygame.font.Font(None, 74)
    fuente_subtitulo = pygame.font.Font(None, 48)
    fuente_botones = pygame.font.Font(None, 36)
    fuente_texto = pygame.font.Font(None, 32)
    fuente_pequena = pygame.font.Font(None, 24)
except:
    fuente_titulo = pygame.font.SysFont("arial", 74)
    fuente_subtitulo = pygame.font.SysFont("arial", 48)
    fuente_botones = pygame.font.SysFont("arial", 36)
    fuente_texto = pygame.font.SysFont("arial", 32)
    fuente_pequena = pygame.font.SysFont("arial", 24)

##########################################
# CLASE BOTÓN PARA INTERFAZ DE USUARIO
##########################################
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_normal, color_hover):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_actual = color_normal
        
    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color_actual, self.rect, border_radius=10)
        pygame.draw.rect(superficie, BLANCO, self.rect, 2, border_radius=10)
        texto_surf = fuente_botones.render(self.texto, True, BLANCO)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        superficie.blit(texto_surf, texto_rect)
        
    def esta_sobre(self, pos):
        if self.rect.collidepoint(pos):
            self.color_actual = self.color_hover
            return True
        else:
            self.color_actual = self.color_normal
            return False

##########################################
# CLASE MINA/TRAMPA DEL JUGADOR
##########################################
class Mina:
    def __init__(self, x, y, tamaño_celda, imagen_mina_escalada=None):
        self.x = x
        self.y = y
        self.tamaño = tamaño_celda // 2
        self.activa = True
        self.tiempo_colocacion = pygame.time.get_ticks()
        self.explotando = False
        self.tiempo_explosion = 0
        self.frame_explosion = 0
        self.radio_explosion = tamaño_celda * 3
        self.duracion_explosion = 800
        self.frame_rate = self.duracion_explosion // len(imagenes_explosion) if imagenes_explosion else 100
        self.tiempo_activacion = 500
        self.jugador_inmune = True
        self.imagen_mina_escalada = imagen_mina_escalada
        
    def dibujar(self, superficie, tamaño_celda):
        if self.explotando:
            if self.frame_explosion < len(imagenes_explosion):
                explosion_img = imagenes_explosion[self.frame_explosion]
                tamaño_explosion = self.radio_explosion * 2
                explosion_escalada = pygame.transform.scale(explosion_img, (tamaño_explosion, tamaño_explosion))
                superficie.blit(explosion_escalada, (self.x - tamaño_explosion // 2, self.y - tamaño_explosion // 2))
        elif self.activa:
            if usar_imagenes and self.imagen_mina_escalada:
                mina_x = self.x - self.tamaño // 2
                mina_y = self.y - self.tamaño // 2
                superficie.blit(self.imagen_mina_escalada, (mina_x, mina_y))
            else:
                pygame.draw.circle(superficie, ROJO_OSCURO, (int(self.x), int(self.y)), self.tamaño)
                pygame.draw.circle(superficie, NEGRO, (int(self.x), int(self.y)), self.tamaño - 3)
                pygame.draw.circle(superficie, AMARILLO, (int(self.x), int(self.y)), 3)
    
    def actualizar(self):
        if self.jugador_inmune and pygame.time.get_ticks() - self.tiempo_colocacion > self.tiempo_activacion:
            self.jugador_inmune = False
            
        if self.explotando:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.tiempo_explosion > self.frame_rate:
                self.frame_explosion += 1
                self.tiempo_explosion = tiempo_actual
            if self.frame_explosion >= len(imagenes_explosion):
                return False
        return True
    
    def explotar(self):
        if not self.explotando and self.activa:
            self.explotando = True
            self.activa = False
            self.tiempo_explosion = pygame.time.get_ticks()
            self.frame_explosion = 0
            return True
        return False
    
    def esta_en_rango_explosion(self, x, y, radio_objeto, es_jugador=False):
        if not self.explotando:
            return False
        if es_jugador and self.jugador_inmune:
            return False
        if self.frame_explosion >= len(imagenes_explosion) // 2:
            return False
        distancia = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distancia < self.radio_explosion + radio_objeto

##########################################
# CLASE CAZADOR (ENEMIGO)
##########################################
class Cazador:
    def __init__(self, x, y, tamaño_celda):
        self.x = x
        self.y = y
        self.tamaño = tamaño_celda // 3
        self.velocidad = tamaño_celda // 15
        self.velocidad_persecucion = tamaño_celda // 12
        self.direccion = [0, 0]
        self.tiempo_cambio_direccion = 0
        self.color = NARANJA
        self.ultima_posicion_jugador = (x, y)
        self.tiempo_ultima_deteccion = 0
        self.modo_persecucion = False
        self.contador_pasos = 0
        self.camino = []
        self.vivo = True
        self.tiempo_muerte = 0
        self.tiempo_respawn = 4000
        
    def puede_pasar_terreno(self, tipo_terreno):
        return tipo_terreno == 0 or tipo_terreno == 2
        
    def encontrar_camino_corto(self, inicio, objetivo, mapa, tamaño_celda):
        filas = len(mapa)
        columnas = len(mapa[0])
        inicio_celda = (int(inicio[1] // tamaño_celda), int(inicio[0] // tamaño_celda))
        objetivo_celda = (int(objetivo[1] // tamaño_celda), int(objetivo[0] // tamaño_celda))
        
        if inicio_celda == objetivo_celda:
            return []
        
        cola = [(inicio_celda, [])]
        visitados = set([inicio_celda])
        direcciones = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while cola:
            (fila_actual, col_actual), camino = cola.pop(0)
            for df, dc in direcciones:
                nueva_fila, nueva_col = fila_actual + df, col_actual + dc
                if (0 <= nueva_fila < filas and 0 <= nueva_col < columnas and
                    (nueva_fila, nueva_col) not in visitados and
                    self.puede_pasar_terreno(mapa[nueva_fila][nueva_col])):
                    nuevo_camino = camino + [(nueva_fila, nueva_col)]
                    if (nueva_fila, nueva_col) == objetivo_celda:
                        return nuevo_camino
                    cola.append(((nueva_fila, nueva_col), nuevo_camino))
                    visitados.add((nueva_fila, nueva_col))
        return []
    
    def mover_hacia_objetivo(self, objetivo_x, objetivo_y, mapa, tamaño_celda):
        if not self.vivo:
            return
            
        distancia_objetivo = math.sqrt((self.x - objetivo_x)**2 + (self.y - objetivo_y)**2)
        if (not self.camino or self.contador_pasos >= 20 or distancia_objetivo > tamaño_celda * 3):
            self.camino = self.encontrar_camino_corto((self.x, self.y), (objetivo_x, objetivo_y), mapa, tamaño_celda)
            self.contador_pasos = 0
        
        if self.camino:
            siguiente_celda = self.camino[0]
            objetivo_x_celda = siguiente_celda[1] * tamaño_celda + tamaño_celda // 2
            objetivo_y_celda = siguiente_celda[0] * tamaño_celda + tamaño_celda // 2
            dx = objetivo_x_celda - self.x
            dy = objetivo_y_celda - self.y
            distancia = math.sqrt(dx*dx + dy*dy)
            
            if distancia > 0:
                dx, dy = dx/distancia, dy/distancia
                nueva_x = self.x + dx * self.velocidad_persecucion
                nueva_y = self.y + dy * self.velocidad_persecucion
                celda_actual_x = int(self.x // tamaño_celda)
                celda_actual_y = int(self.y // tamaño_celda)
                
                if (celda_actual_x == siguiente_celda[1] and celda_actual_y == siguiente_celda[0]):
                    self.camino.pop(0)
                
                celda_x = int(nueva_x // tamaño_celda)
                celda_y = int(nueva_y // tamaño_celda)
                if (0 <= celda_y < len(mapa) and 0 <= celda_x < len(mapa[0])):
                    if self.puede_pasar_terreno(mapa[celda_y][celda_x]):
                        self.x = nueva_x
                        self.y = nueva_y
                        self.contador_pasos += 1
        else:
            self.mover_aleatorio(mapa, tamaño_celda)
    
    def mover_aleatorio(self, mapa, tamaño_celda):
        if not self.vivo:
            return
            
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_cambio_direccion > random.randint(800, 1500):
            direcciones = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            self.direccion = random.choice(direcciones)
            self.tiempo_cambio_direccion = tiempo_actual
        
        nueva_x = self.x + self.direccion[0] * self.velocidad
        nueva_y = self.y + self.direccion[1] * self.velocidad
        celda_x = int(nueva_x // tamaño_celda)
        celda_y = int(nueva_y // tamaño_celda)
        
        movimiento_valido = False
        if (0 <= celda_y < len(mapa) and 0 <= celda_x < len(mapa[0])):
            if self.puede_pasar_terreno(mapa[celda_y][celda_x]):
                self.x = nueva_x
                self.y = nueva_y
                movimiento_valido = True
        
        if not movimiento_valido:
            self.direccion = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
            self.tiempo_cambio_direccion = tiempo_actual
    
    def perseguir_jugador(self, jugador_x, jugador_y, mapa, tamaño_celda):
        if not self.vivo:
            return
            
        distancia = math.sqrt((jugador_x - self.x)**2 + (jugador_y - self.y)**2)
        if distancia < tamaño_celda * 5:
            self.modo_persecucion = True
            self.ultima_posicion_jugador = (jugador_x, jugador_y)
            self.tiempo_ultima_deteccion = pygame.time.get_ticks()
            self.mover_hacia_objetivo(jugador_x, jugador_y, mapa, tamaño_celda)
        else:
            tiempo_desde_deteccion = pygame.time.get_ticks() - self.tiempo_ultima_deteccion
            if self.modo_persecucion and tiempo_desde_deteccion < 3000:
                self.mover_hacia_objetivo(self.ultima_posicion_jugador[0], self.ultima_posicion_jugador[1], mapa, tamaño_celda)
            else:
                self.modo_persecucion = False
                self.mover_aleatorio(mapa, tamaño_celda)
    
    def huir_del_jugador(self, jugador_x, jugador_y, mapa, tamaño_celda):
        if not self.vivo:
            return
            
        distancia = math.sqrt((jugador_x - self.x)**2 + (jugador_y - self.y)**2)
        if distancia < tamaño_celda * 4:
            dx = self.x - jugador_x
            dy = self.y - jugador_y
            if distancia > 0:
                dx, dy = dx/distancia, dy/distancia
                objetivo_x = self.x + dx * tamaño_celda * 3
                objetivo_y = self.y + dy * tamaño_celda * 3
                self.mover_hacia_objetivo(objetivo_x, objetivo_y, mapa, tamaño_celda)
            else:
                self.mover_aleatorio(mapa, tamaño_celda)
        else:
            self.mover_aleatorio(mapa, tamaño_celda)
    
    def morir(self):
        if self.vivo:
            self.vivo = False
            self.tiempo_muerte = pygame.time.get_ticks()
            return True
        return False
    
    def respawn(self, mapa, tamaño_celda):
        if not self.vivo and pygame.time.get_ticks() - self.tiempo_muerte > self.tiempo_respawn:
            while True:
                cx = random.randint(1, len(mapa[0])-2) * tamaño_celda + tamaño_celda//2
                cy = random.randint(1, len(mapa)-2) * tamaño_celda + tamaño_celda//2
                celda_x = int(cx // tamaño_celda)
                celda_y = int(cy // tamaño_celda)
                if mapa[celda_y][celda_x] in [0, 2]:
                    self.x = cx
                    self.y = cy
                    self.vivo = True
                    self.modo_persecucion = False
                    self.camino = []
                    return True
        return False
    
    def dibujar(self, superficie, tamaño_skin, imagen_escalada=None):
        if not self.vivo:
            return
            
        if usar_imagenes and imagen_escalada:
            skin_x = self.x - tamaño_skin // 2
            skin_y = self.y - tamaño_skin // 2
            superficie.blit(imagen_escalada, (skin_x, skin_y))
            if self.modo_persecucion:
                indicador = pygame.Surface((10, 10))
                indicador.fill(ROJO)
                superficie.blit(indicador, (self.x - 5, self.y - self.tamaño - 15))
        else:
            pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.tamaño)
            if self.modo_persecucion:
                pygame.draw.circle(superficie, ROJO, (int(self.x), int(self.y - self.tamaño - 8)), 4)

##########################################
# CREACIÓN DE BOTONES DEL MENÚ PRINCIPAL
##########################################
ancho_boton = 300
alto_boton = 60
espacio_botones = 20
centro_x = ANCHO // 2

boton_escapar = Boton(centro_x - ancho_boton//2, 250, ancho_boton, alto_boton, "🔓 MODO ESCAPAR", AZUL, AZUL_HOVER)
boton_cazar = Boton(centro_x - ancho_boton//2, 250 + alto_boton + espacio_botones, ancho_boton, alto_boton, "🎯 MODO CAZADOR", VERDE, (0, 200, 0))
boton_puntuaciones = Boton(centro_x - ancho_boton//2, 250 + (alto_boton + espacio_botones) * 2, ancho_boton, alto_boton, "🏆 PUNTUACIONES", GRIS_OSCURO, GRIS)
boton_salir = Boton(centro_x - ancho_boton//2, 250 + (alto_boton + espacio_botones) * 3, ancho_boton, alto_boton, "❌ SALIR", ROJO, (200, 0, 0))

##########################################
# CAMPO DE TEXTO PARA REGISTRO DE JUGADOR
##########################################
campo_nombre_rect = pygame.Rect(centro_x - 200, 300, 400, 50)
campo_nombre_activo = False
texto_nombre = ""

##########################################
# GENERACIÓN PROCEDURAL DE LABERINTOS
##########################################
def generar_laberinto(filas, columnas):
    laberinto = [[1 for _ in range(columnas)] for _ in range(filas)]
    
    def es_valida(x, y):
        return 0 <= x < filas and 0 <= y < columnas
    
    def obtener_vecinos(x, y):
        vecinos = []
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            nx, ny = x + dx, y + dy
            if es_valida(nx, ny) and laberinto[nx][ny] == 1:
                vecinos.append((nx, ny, x + dx//2, y + dy//2))
        return vecinos
    
    inicio_x, inicio_y = 1, 1
    laberinto[inicio_x][inicio_y] = 0
    pila = [(inicio_x, inicio_y)]
    
    while pila:
        x, y = pila[-1]
        vecinos = obtener_vecinos(x, y)
        if vecinos:
            nx, ny, px, py = random.choice(vecinos)
            laberinto[px][py] = 0
            laberinto[nx][ny] = 0
            pila.append((nx, ny))
        else:
            pila.pop()
    
    salida_x, salida_y = filas - 2, columnas - 2
    laberinto[salida_x][salida_y] = 0
    if laberinto[salida_x-1][salida_y] == 1 and laberinto[salida_x][salida_y-1] == 1:
        laberinto[salida_x-1][salida_y] = 0
    
    return laberinto

def agregar_terrenos_especiales(laberinto):
    filas = len(laberinto)
    columnas = len(laberinto[0])
    for i in range(filas):
        for j in range(columnas):
            if laberinto[i][j] == 1:
                if random.random() < 0.1:
                    laberinto[i][j] = 2  # Lianas
                elif random.random() < 0.08:
                    laberinto[i][j] = 3  # Túneles
    return laberinto

def crear_mapa_aleatorio():
    filas, columnas = 21, 21
    laberinto = generar_laberinto(filas, columnas)
    laberinto = agregar_terrenos_especiales(laberinto)
    return laberinto

# Generar mapa inicial
mapa = crear_mapa_aleatorio()

##########################################
# FUNCIÓN PARA DIBUJAR MENÚ PRINCIPAL
##########################################
def dibujar_menu_principal():
    for y in range(ALTO):
        color = (max(0, 10 - y//50), max(0, 20 - y//40), max(0, 40 - y//30))
        pygame.draw.line(pantalla, color, (0, y), (ANCHO, y))
    
    titulo = fuente_titulo.render("ESCAPA DEL LABERINTO", True, BLANCO)
    subtitulo = fuente_subtitulo.render("Proyecto II - Introducción a la Programación", True, BLANCO)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 100))
    pantalla.blit(subtitulo, (ANCHO//2 - subtitulo.get_width()//2, 170))
    
    boton_escapar.dibujar(pantalla)
    boton_cazar.dibujar(pantalla)
    boton_puntuaciones.dibujar(pantalla)
    boton_salir.dibujar(pantalla)
    
    if nombre_jugador:
        info_jugador = fuente_texto.render(f"Jugador: {nombre_jugador}", True, BLANCO)
        pantalla.blit(info_jugador, (20, ALTO - 40))
    
    modo_actual = "🎨 Modo Imágenes" if usar_imagenes else "🔧 Modo Colores"
    texto_modo = fuente_texto.render(modo_actual, True, BLANCO)
    pantalla.blit(texto_modo, (ANCHO - texto_modo.get_width() - 20, ALTO - 40))

##########################################
# FUNCIÓN PARA DIBUJAR PANTALLA DE REGISTRO
##########################################
def dibujar_pantalla_registro():
    pantalla.fill((30, 30, 60))
    titulo = fuente_titulo.render("REGISTRO DE JUGADOR", True, BLANCO)
    instruccion = fuente_texto.render("Ingresa tu nombre para comenzar:", True, BLANCO)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 150))
    pantalla.blit(instruccion, (ANCHO//2 - instruccion.get_width()//2, 250))
    
    color_campo = AZUL if campo_nombre_activo else GRIS_OSCURO
    pygame.draw.rect(pantalla, color_campo, campo_nombre_rect, border_radius=5)
    pygame.draw.rect(pantalla, BLANCO, campo_nombre_rect, 2, border_radius=5)
    
    texto_surf = fuente_botones.render(texto_nombre, True, BLANCO)
    pantalla.blit(texto_surf, (campo_nombre_rect.x + 10, campo_nombre_rect.y + 10))
    
    if campo_nombre_activo and pygame.time.get_ticks() % 1000 < 500:
        cursor_x = campo_nombre_rect.x + 10 + texto_surf.get_width()
        pygame.draw.line(pantalla, BLANCO, (cursor_x, campo_nombre_rect.y + 10), (cursor_x, campo_nombre_rect.y + campo_nombre_rect.height - 10), 2)
    
    boton_continuar = Boton(ANCHO//2 - 100, 400, 200, 50, "CONTINUAR", VERDE, (0, 200, 0))
    boton_continuar.dibujar(pantalla)
    return boton_continuar

##########################################
# FUNCIÓN PARA DIBUJAR PANTALLA DE PUNTUACIONES
##########################################
def dibujar_pantalla_puntuaciones():
    pantalla.fill((30, 30, 60))
    titulo = fuente_titulo.render("🏆 PUNTUACIONES", True, BLANCO)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 80))
    
    # Mostrar Top 5 Modo Escapar
    subtitulo_escapar = fuente_subtitulo.render("TOP 5 - MODO ESCAPAR", True, AZUL)
    pantalla.blit(subtitulo_escapar, (ANCHO//4 - subtitulo_escapar.get_width()//2, 150))
    y_pos = 220
    if puntuaciones_escapar:
        for i, puntuacion in enumerate(puntuaciones_escapar[:5]):
            texto = f"{i+1}. {puntuacion['nombre']}: {puntuacion['puntos']} pts"
            texto_surf = fuente_texto.render(texto, True, BLANCO)
            pantalla.blit(texto_surf, (ANCHO//4 - texto_surf.get_width()//2, y_pos))
            y_pos += 40
    else:
        texto_vacio = fuente_texto.render("No hay puntuaciones", True, BLANCO)
        pantalla.blit(texto_vacio, (ANCHO//4 - texto_vacio.get_width()//2, 220))
    
    # Mostrar Top 5 Modo Cazador
    subtitulo_cazador = fuente_subtitulo.render("TOP 5 - MODO CAZADOR", True, VERDE)
    pantalla.blit(subtitulo_cazador, (3*ANCHO//4 - subtitulo_cazador.get_width()//2, 150))
    y_pos = 220
    if puntuaciones_cazador:
        for i, puntuacion in enumerate(puntuaciones_cazador[:5]):
            texto = f"{i+1}. {puntuacion['nombre']}: {puntuacion['puntos']} pts"
            texto_surf = fuente_texto.render(texto, True, BLANCO)
            pantalla.blit(texto_surf, (3*ANCHO//4 - texto_surf.get_width()//2, y_pos))
            y_pos += 40
    else:
        texto_vacio = fuente_texto.render("No hay puntuaciones", True, BLANCO)
        pantalla.blit(texto_vacio, (3*ANCHO//4 - texto_vacio.get_width()//2, 220))
    
    instruccion = fuente_texto.render("Presiona ESC para volver al menú", True, BLANCO)
    pantalla.blit(instruccion, (ANCHO//2 - instruccion.get_width()//2, ALTO - 100))

##########################################
# FUNCIÓN PARA GUARDAR PUNTUACIONES
##########################################
def guardar_puntuacion(nombre, puntos, modo):
    if modo == "MODO ESCAPAR":
        puntuaciones_escapar.append({
            "nombre": nombre,
            "puntos": puntos,
            "modo": modo,
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        puntuaciones_escapar.sort(key=lambda x: x["puntos"], reverse=True)
        if len(puntuaciones_escapar) > 5:
            puntuaciones_escapar.pop()
    else:
        puntuaciones_cazador.append({
            "nombre": nombre,
            "puntos": puntos,
            "modo": modo,
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        puntuaciones_cazador.sort(key=lambda x: x["puntos"], reverse=True)
        if len(puntuaciones_cazador) > 5:
            puntuaciones_cazador.pop()
    
    try:
        with open("puntuaciones.txt", "w") as f:
            f.write("MODO ESCAPAR\n")
            for punt in puntuaciones_escapar:
                f.write(f"{punt['nombre']},{punt['puntos']},{punt['fecha']}\n")
            f.write("MODO CAZADOR\n")
            for punt in puntuaciones_cazador:
                f.write(f"{punt['nombre']},{punt['puntos']},{punt['fecha']}\n")
    except:
        print("⚠️ No se pudo guardar las puntuaciones en archivo")

##########################################
# FUNCIÓN PRINCIPAL DEL JUEGO
##########################################
def jugar_modo(jugador_color, modo_nombre, generar_nuevo_mapa=True):
    global estado_actual, mapa
    
    if generar_nuevo_mapa:
        mapa = crear_mapa_aleatorio()
    
    tamaño_celda = min(ANCHO // len(mapa[0]), ALTO // len(mapa))
    
    if usar_imagenes:
        imagen_muro_escalada = pygame.transform.scale(imagen_muro, (tamaño_celda, tamaño_celda))
        imagen_suelo_escalada = pygame.transform.scale(imagen_suelo, (tamaño_celda, tamaño_celda))
        mina_tamaño = tamaño_celda // 2
        if imagen_mina_original:
            imagen_mina_escalada = pygame.transform.scale(imagen_mina_original, (mina_tamaño, mina_tamaño))
        else:
            imagen_mina_escalada = None
    
    jugador_x = tamaño_celda + tamaño_celda // 2
    jugador_y = tamaño_celda + tamaño_celda // 2
    jugador_tamaño = tamaño_celda // 3
    velocidad = tamaño_celda // 8
    
    tamaño_skin = int(tamaño_celda * 1.2)
    if usar_imagenes and imagen_jugador:
        imagen_jugador_escalada = pygame.transform.scale(imagen_jugador, (tamaño_skin, tamaño_skin))
    if usar_imagenes and imagen_cazador:
        imagen_cazador_escalada = pygame.transform.scale(imagen_cazador, (tamaño_skin, tamaño_skin))
    
    salida_x = (len(mapa[0]) - 2) * tamaño_celda + tamaño_celda // 2
    salida_y = (len(mapa) - 2) * tamaño_celda + tamaño_celda // 2
    
    cazadores = []
    num_cazadores = 3 if modo_nombre == "MODO ESCAPAR" else 5
    
    for _ in range(num_cazadores):
        while True:
            cx = random.randint(1, len(mapa[0])-2) * tamaño_celda + tamaño_celda//2
            cy = random.randint(1, len(mapa)-2) * tamaño_celda + tamaño_celda//2
            celda_x = int(cx // tamaño_celda)
            celda_y = int(cy // tamaño_celda)
            if mapa[celda_y][celda_x] in [0, 2]:
                cazadores.append(Cazador(cx, cy, tamaño_celda))
                break
    
    minas = []
    max_minas = 3
    tiempo_ultima_mina = 0
    cooldown_mina = 5000
    
    tiempo_inicio = pygame.time.get_ticks()
    tiempo_final = 0
    tiempo_limite_base = 15000
    puntuacion_base = 1500
    penalizacion_por_segundo = 25
    puntos_por_cazador = 250
    
    energia = 100
    energia_maxima = 100
    corriendo = False
    juego_terminado = False
    resultado = ""
    puntuacion_final = 0
    cazadores_eliminados = 0
    
    def puede_pasar_terreno_jugador(tipo_terreno, es_modo_cazador):
        if es_modo_cazador:
            return tipo_terreno == 0 or tipo_terreno == 2
        else:
            return tipo_terreno == 0 or tipo_terreno == 3
    
    def hay_colision(x, y, es_jugador=True):
        puntos_verificacion = [
            (x, y),
            (x - jugador_tamaño//2, y),
            (x + jugador_tamaño//2, y),
            (x, y - jugador_tamaño//2),
            (x, y + jugador_tamaño//2),
        ]
        for px, py in puntos_verificacion:
            celda_x = int(px // tamaño_celda)
            celda_y = int(py // tamaño_celda)
            if (celda_y < 0 or celda_y >= len(mapa) or celda_x < 0 or celda_x >= len(mapa[0])):
                return True
            tipo_terreno = mapa[celda_y][celda_x]
            es_modo_cazador_jugador = (modo_nombre == "MODO CAZADOR" and es_jugador)
            if not puede_pasar_terreno_jugador(tipo_terreno, es_modo_cazador_jugador):
                return True
        return False
    
    def verificar_salida():
        distancia_x = abs(jugador_x - salida_x)
        distancia_y = abs(jugador_y - salida_y)
        return distancia_x < tamaño_celda and distancia_y < tamaño_celda
    
    def verificar_colision_cazadores():
        for cazador in cazadores:
            if cazador.vivo:
                distancia = math.sqrt((jugador_x - cazador.x)**2 + (jugador_y - cazador.y)**2)
                if distancia < jugador_tamaño + cazador.tamaño:
                    return True
        return False
    
    def colocar_mina():
        tiempo_actual = pygame.time.get_ticks()
        minas_activas = sum(1 for mina in minas if mina.activa and not mina.explotando)
        if (minas_activas < max_minas and tiempo_actual - tiempo_ultima_mina > cooldown_mina):
            nueva_mina = Mina(jugador_x, jugador_y, tamaño_celda, imagen_mina_escalada)
            minas.append(nueva_mina)
            return True
        return False
    
    def activar_minas_cercanas():
        minas_activadas = 0
        for mina in minas:
            if mina.activa and not mina.explotando:
                for cazador in cazadores:
                    if cazador.vivo:
                        distancia_cazador = math.sqrt((cazador.x - mina.x)**2 + (cazador.y - mina.y)**2)
                        if distancia_cazador < mina.radio_explosion:
                            mina.explotar()
                            minas_activadas += 1
                            break
        return minas_activadas
    
    def verificar_explosiones():
        jugador_muerto = False
        cazadores_eliminados_esta_ronda = 0
        activar_minas_cercanas()
        for mina in minas[:]:
            if not mina.actualizar():
                minas.remove(mina)
                continue
            if mina.explotando:
                for cazador in cazadores:
                    if cazador.vivo and mina.esta_en_rango_explosion(cazador.x, cazador.y, cazador.tamaño, es_jugador=False):
                        if cazador.morir():
                            cazadores_eliminados_esta_ronda += 1
        return jugador_muerto, cazadores_eliminados_esta_ronda
    
    def calcular_puntuacion(tiempo_transcurrido):
        tiempo_segundos = tiempo_transcurrido // 1000
        if tiempo_segundos <= 15:
            puntos_tiempo = puntuacion_base
        else:
            segundos_extra = tiempo_segundos - 15
            penalizacion_total = segundos_extra * penalizacion_por_segundo
            puntos_tiempo = max(0, puntuacion_base - penalizacion_total)
        puntos_cazadores = cazadores_eliminados * puntos_por_cazador
        return puntos_tiempo + puntos_cazadores
    
    ejecutando_juego = True
    while ejecutando_juego:
        tiempo_actual = pygame.time.get_ticks()
        if juego_terminado:
            tiempo_transcurrido = tiempo_final
        else:
            tiempo_transcurrido = tiempo_actual - tiempo_inicio
        
        reloj.tick(60)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando_juego = False
                estado_actual = MENU_PRINCIPAL
                return
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando_juego = False
                    estado_actual = MENU_PRINCIPAL
                    return
                elif evento.key == pygame.K_LSHIFT and not juego_terminado:
                    corriendo = True
                elif evento.key == pygame.K_r and juego_terminado:
                    return jugar_modo(jugador_color, modo_nombre, True)
                elif evento.key == pygame.K_TAB and not juego_terminado:
                    if colocar_mina():
                        tiempo_ultima_mina = pygame.time.get_ticks()
            elif evento.type == pygame.KEYUP:
                if evento.key == pygame.K_LSHIFT:
                    corriendo = False
        
        if not juego_terminado:
            for cazador in cazadores:
                if cazador.vivo:
                    if modo_nombre == "MODO ESCAPAR":
                        cazador.perseguir_jugador(jugador_x, jugador_y, mapa, tamaño_celda)
                    else:
                        cazador.huir_del_jugador(jugador_x, jugador_y, mapa, tamaño_celda)
                else:
                    cazador.respawn(mapa, tamaño_celda)
            
            _, nuevos_eliminados = verificar_explosiones()
            cazadores_eliminados += nuevos_eliminados
            
            if verificar_colision_cazadores():
                if modo_nombre == "MODO ESCAPAR":
                    juego_terminado = True
                    resultado = "¡TE ATRAPARON!"
                    puntuacion_final = 0
                    tiempo_final = tiempo_transcurrido
                else:
                    for i, cazador in enumerate(cazadores):
                        if cazador.vivo:
                            distancia = math.sqrt((jugador_x - cazador.x)**2 + (jugador_y - cazador.y)**2)
                            if distancia < jugador_tamaño + cazador.tamaño:
                                if cazador.morir():
                                    cazadores_eliminados += 1
                                break
            
            velocidad_actual = velocidad
            if corriendo and energia > 0:
                velocidad_actual = velocidad * 2
                energia -= 0.8
            elif not corriendo and energia < energia_maxima:
                energia += 0.3
            
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_LEFT]:
                nueva_x = jugador_x - velocidad_actual
                if not hay_colision(nueva_x, jugador_y):
                    jugador_x = nueva_x
            if teclas[pygame.K_RIGHT]:
                nueva_x = jugador_x + velocidad_actual
                if not hay_colision(nueva_x, jugador_y):
                    jugador_x = nueva_x
            if teclas[pygame.K_UP]:
                nueva_y = jugador_y - velocidad_actual
                if not hay_colision(jugador_x, nueva_y):
                    jugador_y = nueva_y
            if teclas[pygame.K_DOWN]:
                nueva_y = jugador_y + velocidad_actual
                if not hay_colision(jugador_x, nueva_y):
                    jugador_y = nueva_y
            
            if verificar_salida():
                juego_terminado = True
                resultado = "¡ESCAPASTE!" if modo_nombre == "MODO ESCAPAR" else "¡VICTORIA!"
                tiempo_final = tiempo_transcurrido
                puntuacion_final = calcular_puntuacion(tiempo_final)
                guardar_puntuacion(nombre_jugador, puntuacion_final, modo_nombre)
        
        pantalla.fill(NEGRO)
        
        for fila in range(len(mapa)):
            for columna in range(len(mapa[0])):
                x = columna * tamaño_celda
                y = fila * tamaño_celda
                if mapa[fila][columna] == 0:
                    if usar_imagenes:
                        pantalla.blit(imagen_suelo_escalada, (x, y))
                    else:
                        pygame.draw.rect(pantalla, GRIS, (x, y, tamaño_celda, tamaño_celda))
                elif mapa[fila][columna] == 1:
                    if usar_imagenes:
                        pantalla.blit(imagen_muro_escalada, (x, y))
                    else:
                        pygame.draw.rect(pantalla, BLANCO, (x, y, tamaño_celda, tamaño_celda))
                elif mapa[fila][columna] == 2:
                    if usar_imagenes:
                        pantalla.blit(imagen_muro_escalada, (x, y))
                        lianas_surface = pygame.Surface((tamaño_celda, tamaño_celda), pygame.SRCALPHA)
                        lianas_surface.fill((0, 100, 0, 150))
                        pantalla.blit(lianas_surface, (x, y))
                    else:
                        pygame.draw.rect(pantalla, VERDE_OSCURO, (x, y, tamaño_celda, tamaño_celda))
                elif mapa[fila][columna] == 3:
                    if usar_imagenes:
                        pantalla.blit(imagen_muro_escalada, (x, y))
                        tunel_surface = pygame.Surface((tamaño_celda, tamaño_celda), pygame.SRCALPHA)
                        tunel_surface.fill((100, 100, 255, 150))
                        pantalla.blit(tunel_surface, (x, y))
                    else:
                        pygame.draw.rect(pantalla, AZUL_CLARO, (x, y, tamaño_celda, tamaño_celda))
        
        salida_rect = pygame.Rect((len(mapa[0]) - 2) * tamaño_celda, (len(mapa) - 2) * tamaño_celda, tamaño_celda, tamaño_celda)
        pygame.draw.rect(pantalla, VERDE, salida_rect)
        
        for mina in minas:
            mina.dibujar(pantalla, tamaño_celda)
        
        for cazador in cazadores:
            cazador.dibujar(pantalla, tamaño_skin, imagen_cazador_escalada if usar_imagenes else None)
        
        if usar_imagenes and imagen_jugador:
            skin_x = jugador_x - tamaño_skin // 2
            skin_y = jugador_y - tamaño_skin // 2
            pantalla.blit(imagen_jugador_escalada, (skin_x, skin_y))
        else:
            pygame.draw.circle(pantalla, jugador_color, (int(jugador_x), int(jugador_y)), jugador_tamaño)
        
        barra_ancho = 200
        barra_alto = 20
        barra_x = 20
        barra_y = 20
        
        pygame.draw.rect(pantalla, (50, 50, 50), (barra_x, barra_y, barra_ancho, barra_alto))
        energia_ancho = (energia / energia_maxima) * barra_ancho
        color_energia = (0, 255, 0) if energia > 30 else (255, 0, 0)
        pygame.draw.rect(pantalla, color_energia, (barra_x, barra_y, energia_ancho, barra_alto))
        pygame.draw.rect(pantalla, BLANCO, (barra_x, barra_y, barra_ancho, barra_alto), 2)
        
        minas_activas = sum(1 for mina in minas if mina.activa and not mina.explotando)
        tiempo_restante = max(0, cooldown_mina - (pygame.time.get_ticks() - tiempo_ultima_mina))
        puede_colocar = minas_activas < max_minas and tiempo_restante == 0
        
        texto_minas = fuente_texto.render(f"Minas: {minas_activas}/{max_minas}", True, BLANCO)
        pantalla.blit(texto_minas, (20, 50))
        
        if tiempo_restante > 0:
            texto_cooldown = fuente_pequena.render(f"CD: {tiempo_restante//1000}s", True, ROJO)
            pantalla.blit(texto_cooldown, (20, 75))
        elif puede_colocar:
            texto_listo = fuente_pequena.render("TAB: Colocar mina", True, VERDE)
            pantalla.blit(texto_listo, (20, 75))
        
        tiempo_segundos = tiempo_transcurrido // 1000
        tiempo_milisegundos = (tiempo_transcurrido % 1000) // 10
        texto_tiempo = fuente_texto.render(f"Tiempo: {tiempo_segundos}.{tiempo_milisegundos:02d}s", True, BLANCO)
        pantalla.blit(texto_tiempo, (ANCHO - texto_tiempo.get_width() - 20, 100))
        
        if not juego_terminado:
            puntuacion_actual = calcular_puntuacion(tiempo_transcurrido)
            texto_puntos = fuente_texto.render(f"Puntos: {puntuacion_actual}", True, AMARILLO)
            pantalla.blit(texto_puntos, (ANCHO - texto_puntos.get_width() - 20, 130))
        
        texto_cazadores_eliminados = fuente_texto.render(f"Cazadores: {cazadores_eliminados}", True, BLANCO)
        pantalla.blit(texto_cazadores_eliminados, (ANCHO - texto_cazadores_eliminados.get_width() - 20, 160))
        
        texto_modo = fuente_botones.render(f"{modo_nombre} - ESC: Menú | R: Reiniciar", True, BLANCO)
        pantalla.blit(texto_modo, (ANCHO//2 - texto_modo.get_width()//2, 20))
        
        cazadores_vivos = sum(1 for c in cazadores if c.vivo)
        texto_cazadores = fuente_texto.render(f"Cazadores vivos: {cazadores_vivos}/{len(cazadores)}", True, BLANCO)
        pantalla.blit(texto_cazadores, (ANCHO - texto_cazadores.get_width() - 20, 60))
        
        if nombre_jugador:
            texto_jugador = fuente_texto.render(f"Jugador: {nombre_jugador}", True, BLANCO)
            pantalla.blit(texto_jugador, (ANCHO - texto_jugador.get_width() - 20, 20))
        
        modo_texto = "🎨 Modo Imágenes" if usar_imagenes else "🔧 Modo Colores"
        texto_modo_actual = fuente_texto.render(modo_texto, True, BLANCO)
        pantalla.blit(texto_modo_actual, (20, ALTO - 40))
        
        if modo_nombre == "MODO CAZADOR":
            info_terreno = fuente_texto.render("Modo Cazador: Solo caminos y lianas", True, AMARILLO)
            pantalla.blit(info_terreno, (ANCHO//2 - info_terreno.get_width()//2, 60))
        
        if juego_terminado:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            pantalla.blit(overlay, (0, 0))
            resultado_font = pygame.font.Font(None, 72)
            resultado_text = resultado_font.render(resultado, True, BLANCO)
            pantalla.blit(resultado_text, (ANCHO//2 - resultado_text.get_width()//2, ALTO//2 - 100))
            
            if puntuacion_final > 0:
                puntuacion_font = pygame.font.Font(None, 48)
                puntuacion_text = puntuacion_font.render(f"Puntuación: {puntuacion_final} puntos", True, AMARILLO)
                pantalla.blit(puntuacion_text, (ANCHO//2 - puntuacion_text.get_width()//2, ALTO//2 - 30))
                tiempo_segundos = tiempo_final // 1000
                if tiempo_segundos <= 15:
                    tiempo_text = fuente_texto.render(f"Tiempo: {tiempo_segundos}s (+{puntuacion_base} pts)", True, VERDE)
                else:
                    segundos_extra = tiempo_segundos - 15
                    penalizacion = segundos_extra * penalizacion_por_segundo
                    tiempo_text = fuente_texto.render(f"Tiempo: {tiempo_segundos}s (-{penalizacion} pts)", True, ROJO)
                cazadores_text = fuente_texto.render(f"Cazadores eliminados: {cazadores_eliminados} (+{cazadores_eliminados * puntos_por_cazador} pts)", True, VERDE)
                pantalla.blit(tiempo_text, (ANCHO//2 - tiempo_text.get_width()//2, ALTO//2 + 20))
                pantalla.blit(cazadores_text, (ANCHO//2 - cazadores_text.get_width()//2, ALTO//2 + 50))
            
            instruccion_font = pygame.font.Font(None, 36)
            instruccion_text = instruccion_font.render("Presiona R para reiniciar o ESC para volver al menú", True, BLANCO)
            pantalla.blit(instruccion_text, (ANCHO//2 - instruccion_text.get_width()//2, ALTO//2 + 100))
        
        pygame.display.flip()

##########################################
# FUNCIÓN PARA CARGAR PUNTUACIONES GUARDADAS
##########################################
def cargar_puntuaciones():
    global puntuaciones_escapar, puntuaciones_cazador
    try:
        if os.path.exists("puntuaciones.txt"):
            modo_actual = None
            with open("puntuaciones.txt", "r") as f:
                for linea in f:
                    linea = linea.strip()
                    if linea == "MODO ESCAPAR":
                        modo_actual = "MODO ESCAPAR"
                    elif linea == "MODO CAZADOR":
                        modo_actual = "MODO CAZADOR"
                    elif linea and modo_actual:
                        partes = linea.split(",")
                        if len(partes) >= 2:
                            puntuacion = {
                                "nombre": partes[0],
                                "puntos": int(partes[1]),
                                "modo": modo_actual,
                                "fecha": partes[2] if len(partes) > 2 else "Desconocida"
                            }
                            if modo_actual == "MODO ESCAPAR":
                                puntuaciones_escapar.append(puntuacion)
                            else:
                                puntuaciones_cazador.append(puntuacion)
            puntuaciones_escapar.sort(key=lambda x: x["puntos"], reverse=True)
            puntuaciones_escapar = puntuaciones_escapar[:5]
            puntuaciones_cazador.sort(key=lambda x: x["puntos"], reverse=True)
            puntuaciones_cazador = puntuaciones_cazador[:5]
    except Exception as e:
        print(f"⚠️ No se pudieron cargar las puntuaciones anteriores: {e}")

cargar_puntuaciones()

##########################################
# BUCLE PRINCIPAL DEL JUEGO
##########################################
ejecutando = True
while ejecutando:
    mouse_pos = pygame.mouse.get_pos()
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if estado_actual in [MODO_ESCAPA, MODO_CAZADOR, PUNTUACIONES]:
                    estado_actual = MENU_PRINCIPAL
                else:
                    ejecutando = False
            if estado_actual == REGISTRO:
                if evento.key == pygame.K_RETURN:
                    if texto_nombre.strip():
                        nombre_jugador = texto_nombre.strip()
                        estado_actual = MENU_PRINCIPAL
                elif evento.key == pygame.K_BACKSPACE:
                    texto_nombre = texto_nombre[:-1]
                else:
                    if len(texto_nombre) < 20:
                        texto_nombre += evento.unicode
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if estado_actual == MENU_PRINCIPAL:
                if boton_escapar.esta_sobre(mouse_pos):
                    if nombre_jugador:
                        estado_actual = MODO_ESCAPA
                    else:
                        estado_actual = REGISTRO
                elif boton_cazar.esta_sobre(mouse_pos):
                    if nombre_jugador:
                        estado_actual = MODO_CAZADOR
                    else:
                        estado_actual = REGISTRO
                elif boton_puntuaciones.esta_sobre(mouse_pos):
                    estado_actual = PUNTUACIONES
                elif boton_salir.esta_sobre(mouse_pos):
                    ejecutando = False
            elif estado_actual == REGISTRO:
                campo_nombre_activo = campo_nombre_rect.collidepoint(mouse_pos)
                boton_continuar = dibujar_pantalla_registro()
                if boton_continuar.esta_sobre(mouse_pos) and texto_nombre.strip():
                    nombre_jugador = texto_nombre.strip()
                    estado_actual = MENU_PRINCIPAL
    
    if estado_actual == MENU_PRINCIPAL:
        boton_escapar.esta_sobre(mouse_pos)
        boton_cazar.esta_sobre(mouse_pos)
        boton_puntuaciones.esta_sobre(mouse_pos)
        boton_salir.esta_sobre(mouse_pos)
    
    if estado_actual == MENU_PRINCIPAL:
        dibujar_menu_principal()
    elif estado_actual == REGISTRO:
        dibujar_pantalla_registro()
    elif estado_actual == MODO_ESCAPA:
        jugar_modo(AZUL, "MODO ESCAPAR", True)
    elif estado_actual == MODO_CAZADOR:
        jugar_modo(ROJO, "MODO CAZADOR", True)
    elif estado_actual == PUNTUACIONES:
        dibujar_pantalla_puntuaciones()
    
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()