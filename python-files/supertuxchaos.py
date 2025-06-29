from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import *
import sys
import os
import random
import math
import traceback
import json

class SupertuxBattleRoyale(ShowBase):
    def __init__(self):
        print("Iniciando SupertuxBattleRoyale...")
        try:
            ShowBase.__init__(self)
        except Exception as e:
            print(f"Error al inicializar Panda3D: {str(e)}")
            traceback.print_exc()
            input("Presiona Enter para salir...")
            sys.exit(1)
        
        # Configuración básica
        print("Configurando variables iniciales...")
        self.disableMouse()
        self.estado = "menu"
        self.personaje_seleccionado = None
        self.stage_seleccionado = None
        self.personaje = None
        self.rotacion_personaje = 0
        self.musica = None
        self.jugadores = []
        self.max_jugadores = 20
        self.arena_size = 50
        self.shrink_speed = 0.5
        self.shrink_timer = 0
        self.shrink_interval = 10
        self.game_time = 0
        self.game_duration = 300
        self.vidas = 3
        self.puntos = 0
        self.selected_model = None
        self.skybox = None
        self.desafios_desbloqueados = self.cargar_desbloqueos()
        
        # Física
        self.cTrav = None
        self.pusher = None
        self.setup_physics()
        
        # Inicializar UI y recursos
        print("Cargando recursos...")
        self.cargar_recursos()
        print("Creando menú...")
        self.crear_menu()

        # Controles globales
        self.accept("escape", self.salir_juego)
        self.accept("p", self.toggle_pausa)

    def cargar_desbloqueos(self):
        print("Cargando desbloqueos...")
        try:
            if os.path.exists("unlocks.json"):
                with open("unlocks.json", "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando desbloqueos: {str(e)}")
        return {"kitty": False, "proprietary": False, "penny": False}

    def guardar_desbloqueos(self):
        print("Guardando desbloqueos...")
        try:
            with open("unlocks.json", "w") as f:
                json.dump(self.desafios_desbloqueados, f)
        except Exception as e:
            print(f"Error guardando desbloqueos: {str(e)}")

    def setup_physics(self):
        print("Configurando física...")
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.pusher.setHorizontal(True)
        self.safe_zone = None
        self.update_safe_zone()
        
    def update_safe_zone(self):
        print("Actualizando zona segura...")
        if self.safe_zone:
            self.safe_zone.removeNode()
            
        if self.stage_seleccionado:
            modelo_path = f"models/{self.stage_seleccionado}"
            if os.path.exists(modelo_path):
                self.safe_zone = self.loader.loadModel(modelo_path)
            else:
                print(f"Modelo {modelo_path} no encontrado, usando modelo por defecto...")
                self.safe_zone = self.create_simple_box_model()
        else:
            print("No hay stage seleccionado, usando modelo por defecto...")
            self.safe_zone = self.loader.loadModel("models/box.egg") if os.path.exists("models/box.egg") else self.create_simple_box_model()
            
        self.safe_zone.setScale(self.arena_size, self.arena_size, 1)
        self.safe_zone.setPos(0, 0, 0)
        self.safe_zone.reparentTo(self.render)
        
        if self.stage_seleccionado == "box.egg":
            self.safe_zone.setColor(0.2, 0.8, 0.2, 1)
        else:
            self.safe_zone.setColor(1.0, 1.0, 1.0, 1)
            
        cNode = CollisionNode("safe_zone")
        cNode.addSolid(CollisionTube(-self.arena_size/2, 0, 0, self.arena_size/2, 0, 0, 0.5))
        cNode.addSolid(CollisionTube(0, -self.arena_size/2, 0, 0, self.arena_size/2, 0, 0.5))
        cNodePath = self.safe_zone.attachNewNode(cNode)
        cNodePath.setCollideMask(BitMask32.allOn())

    def cargar_recursos(self):
        print("Cargando fuente...")
        try:
            if os.path.exists("models/fuente.ttf"):
                self.fuente = self.loader.loadFont("models/fuente.ttf")
            else:
                print("Fuente TTF no encontrada, usando cmss12.egg...")
                self.fuente = self.loader.loadFont("cmss12.egg")
        except Exception as e:
            print(f"Error cargando recursos de fuente: {str(e)}")
            self.fuente = None

    def create_simple_box_model(self):
        print("Creando modelo de caja simple...")
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData("cube", format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        
        for x in [-0.5, 0.5]:
            for y in [-0.5, 0.5]:
                for z in [-0.5, 0.5]:
                    vertex.addData3f(x, y, z)
        
        prim = GeomTriangles(Geom.UHStatic)
        indices = [
            (0,1,3), (0,3,2), (4,6,7), (4,7,5),
            (0,2,6), (0,6,4), (1,5,7), (1,7,3),
            (0,4,5), (0,5,1), (2,3,7), (2,7,6)
        ]
        for i1, i2, i3 in indices:
            prim.addVertices(i1, i2, i3)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        node = GeomNode("cube")
        node.addGeom(geom)
        cube = NodePath(node)
        cube.writeBamFile("models/box.bam")
        return cube

    def crear_menu(self):
        print("Creando menú principal...")
        self.limpiar_ui()
        self.estado = "menu"
        
        self.titulo = OnscreenText(
            text="SuperTuxChaos",
            parent=base.a2dTopCenter,
            scale=0.08,
            fg=(1, 0.5, 0, 1),
            pos=(0, -0.1),
            font=self.fuente)
        
        self.boton_jugar = DirectButton(
            text="Jugar",
            scale=0.07,
            pos=(0, 0, -0.2),
            command=self.ir_a_seleccion,
            frameColor=(0, 0.6, 0, 0.7),
            text_font=self.fuente)
        
        self.boton_desafios = DirectButton(
            text="Desafíos",
            scale=0.07,
            pos=(0, 0, -0.35),
            command=self.crear_menu_desafios,
            frameColor=(0.6, 0.4, 0.8, 0.7),
            text_font=self.fuente)
        
        self.boton_instrucciones = DirectButton(
            text="Instrucciones",
            scale=0.07,
            pos=(0, 0, -0.5),
            command=self.mostrar_instrucciones,
            frameColor=(0, 0.5, 0.8, 0.7),
            text_font=self.fuente)
        
        self.boton_creditos = DirectButton(
            text="Créditos",
            scale=0.07,
            pos=(0, 0, -0.65),
            command=self.mostrar_creditos,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)
        
        self.boton_salir = DirectButton(
            text="Salir",
            scale=0.07,
            pos=(0, 0, -0.8),
            command=self.salir_juego,
            frameColor=(0.8, 0, 0, 0.7),
            text_font=self.fuente)

        try:
            if os.path.exists("models/music.ogg"):
                print("Cargando música del menú...")
                if self.musica:
                    self.musica.stop()
                self.musica = self.loader.loadMusic("models/music.ogg")
                self.musica.setLoop(True)
                self.musica.play()
        except Exception as e:
            print(f"Error cargando música del menú: {str(e)}")

    def crear_menu_desafios(self):
        print("Creando menú de desafíos...")
        self.limpiar_ui()
        self.estado = "desafios"
        
        self.titulo_desafios = OnscreenText(
            text="Desafíos",
            parent=base.a2dTopCenter,
            scale=0.08,
            fg=(1, 0.5, 0, 1),
            pos=(0, -0.1),
            font=self.fuente)
        
        self.boton_desafio_kitty = DirectButton(
            text="Desafío: Kitty (Cementerio de Software)",
            scale=0.06,
            pos=(0, 0, -0.3),
            command=self.iniciar_desafio_kitty_seleccion,
            frameColor=(0.9, 0.3, 0.3, 0.7),
            text_font=self.fuente)
        
        self.boton_desafio_proprietary = DirectButton(
            text="Desafío: Proprietary (Bliss)" if self.desafios_desbloqueados["kitty"] else "??? (Desbloquea Kitty primero)",
            scale=0.06,
            pos=(0, 0, -0.45),
            command=self.iniciar_desafio_proprietary_seleccion if self.desafios_desbloqueados["kitty"] else None,
            frameColor=(1.0, 0.0, 0.0, 0.7) if self.desafios_desbloqueados["kitty"] else (0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)
        
        self.boton_desafio_aleatorio = DirectButton(
            text="Desafío Aleatorio",
            scale=0.06,
            pos=(0, 0, -0.6),
            command=self.iniciar_desafio_aleatorio_seleccion,
            frameColor=(0.4, 0.8, 0.4, 0.7),
            text_font=self.fuente)
        
        self.boton_atras = DirectButton(
            text="Volver",
            scale=0.06,
            pos=(0, 0, -0.75),
            command=self.crear_menu,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)

    def iniciar_desafio_kitty_seleccion(self):
        self.modo_desafio_proximo = "kitty"
        self.crear_seleccion_personajes(callback=self.pre_iniciar_desafio_kitty)

    def pre_iniciar_desafio_kitty(self):
        if os.path.exists("models/challenge_video.mp4"):
            self.reproducir_video("models/challenge_video.mp4", self.iniciar_juego_kitty)
        else:
            self.iniciar_juego_kitty()

    def iniciar_desafio_proprietary_seleccion(self):
        self.modo_desafio_proximo = "proprietary"
        self.crear_seleccion_personajes(callback=self.iniciar_juego_proprietary)

    def iniciar_desafio_aleatorio_seleccion(self):
        self.modo_desafio_proximo = "aleatorio"
        self.crear_seleccion_personajes(callback=self.iniciar_juego_aleatorio)

    def reproducir_video(self, video_path, callback):
        print(f"Intentando reproducir video: {video_path}")
        try:
            self.limpiar_ui()
            self.estado = "video"
            texture = self.loader.loadTexture(video_path)
            cm = CardMaker("video_card")
            cm.setFrame(-1, 1, -1, 1)
            video_card = self.aspect2d.attachNewNode(cm.generate())
            video_card.setTexture(texture)
            sound = self.loader.loadSfx(video_path)
            sound.play()
            def check_video(task):
                if sound.status() == sound.PLAYING:
                    return task.cont
                else:
                    video_card.removeNode()
                    sound.stop()
                    callback()
                    return task.done
            self.taskMgr.add(check_video, "check_video")
        except Exception as e:
            print(f"Error reproduciendo video: {str(e)}")
            callback()

    def iniciar_juego_kitty(self):
        print("Iniciando juego contra Kitty...")
        self.personaje_seleccionado = self.personaje_seleccionado or "tud"
        self.stage_seleccionado = "cementerio1.glb"
        self.iniciar_juego_desafio("kitty")

    def iniciar_juego_proprietary(self):
        print("Iniciando juego contra Proprietary...")
        self.personaje_seleccionado = self.personaje_seleccionado or "tud"
        self.stage_seleccionado = "box.egg"
        self.iniciar_juego_desafio("proprietary")

    def iniciar_juego_aleatorio(self):
        print("Iniciando juego aleatorio...")
        modelos_disponibles = ["tud", "freedo", "pennyt", "adium", "kongi", "droida", "chuc", "senia", "mint", "xue", "buggie", "pirf", "dika",
                               "propietar", "wilber3", "codee", "bbbfr", "mozallera", "sinbody", "puffy3", "peee", "arf", "duog", "kitty1"]
        stages_disponibles = ["picolibre1.glb", "antartica.glb", "box.egg", "cementerio1.glb"]
        self.personaje_seleccionado = self.personaje_seleccionado or "tud"
        self.stage_seleccionado = random.choice(stages_disponibles)
        self.iniciar_juego_desafio(random.choice(modelos_disponibles))

    def iniciar_juego_desafio(self, oponente):
        print(f"Iniciando desafío contra {oponente}...")
        self.limpiar_ui()
        self.estado = "desafio"
        self.game_time = 0
        self.vidas = 3
        self.puntos = 0
        self.arena_size = 50
        self.update_safe_zone()
        
        # Cargar skybox
        print("Cargando skybox...")
        if self.skybox:
            self.skybox.removeNode()
        skybox_path = None
        if self.stage_seleccionado in ["picolibre1.glb", "box.egg"]:
            skybox_path = "models/sky1.egg"
        elif self.stage_seleccionado == "antartica.glb":
            skybox_path = "models/sky2.egg"
        elif self.stage_seleccionado == "cementerio1.glb":
            skybox_path = "models/sky3.egg"
        
        if skybox_path and os.path.exists(skybox_path):
            print(f"Cargando skybox: {skybox_path}")
            self.skybox = self.loader.loadModel(skybox_path)
            self.skybox.reparentTo(self.render)
            self.skybox.setScale(100)
            self.skybox.setPos(0, 0, 0)
            self.skybox.setBin("background", 0)
            self.skybox.setDepthWrite(False)
            self.skybox.setTwoSided(True)
        else:
            print(f"Skybox {skybox_path} no encontrado.")
        
        try:
            print("Cargando música del juego...")
            if self.musica:
                self.musica.stop()
            if self.stage_seleccionado == "picolibre1.glb" and os.path.exists("models/tk2.ogg"):
                self.musica = self.loader.loadMusic("models/tk2.ogg")
            elif self.stage_seleccionado == "antartica.glb" and os.path.exists("models/chipdisko.ogg"):
                self.musica = self.loader.loadMusic("models/chipdisko.ogg")
            elif self.stage_seleccionado == "cementerio1.glb" and os.path.exists("models/tk5a.ogg"):
                self.musica = self.loader.loadMusic("models/tk5a.ogg")
            elif os.path.exists("models/music.ogg"):
                self.musica = self.loader.loadMusic("models/music.ogg")
            if self.musica:
                self.musica.setLoop(True)
                self.musica.play()
        except Exception as e:
            print(f"Error cargando música del juego: {str(e)}")
            
        modelo_path = f"models/{self.personaje_seleccionado}.glb"
        if os.path.exists(modelo_path):
            print(f"Cargando personaje: {modelo_path}")
            self.personaje = self.loader.loadModel(modelo_path)
            self.personaje.reparentTo(self.render)
            self.personaje.setPos(0, 0, 0.5)
            self.personaje.setScale(1.2)
            
            cNode = CollisionNode("player")
            cNode.addSolid(CollisionSphere(0, 0, 0.5, 0.8))
            cNodePath = self.personaje.attachNewNode(cNode)
            self.cTrav.addCollider(cNodePath, self.pusher)
            self.pusher.addCollider(cNodePath, self.personaje)
            
            self.camera.setPos(self.personaje.getX(), self.personaje.getY() - 15, 3)
            self.camera.lookAt(self.personaje)
            self.taskMgr.add(self.update_camera, "update_camera")
            
            self.crear_oponente_desafio(oponente)
            
            self.crear_ui_juego()
            
            self.accept("w", self.mover_adelante)
            self.accept("a", self.mover_izquierda)
            self.accept("s", self.mover_atras)
            self.accept("d", self.mover_derecha)
            self.accept("space", self.empujar)
            self.accept("escape", self.toggle_pausa)
            self.accept("p", self.toggle_pausa)
            
            self.taskMgr.add(self.update_desafio, "update_desafio")
            self.taskMgr.add(self.check_boundaries, "check_boundaries")
        else:
            print(f"Error: Modelo del personaje {modelo_path} no encontrado.")
            self.fin_del_desafio(ganador=False)

    def crear_oponente_desafio(self, oponente):
        print(f"Creando oponente: {oponente}")
        self.jugadores = []
        npc = {
            "modelo": None,
            "velocidad": 2.0,
            "direccion": random.uniform(0, 360),
            "fuerza": 2.0,
            "activo": True,
            "invulnerable": 0,
            "push_timer": 1.5,
            "salud": 20,
            "tipo": oponente
        }
        
        modelo_path = ""
        if oponente == "kitty":
            modelo_path = "models/kitty1.glb" # Usar el modelo GLB de kitty1
        elif oponente == "proprietary":
            modelo_path = "models/propietar.glb"
        else:
            modelo_path = f"models/{oponente}.glb" # Para desafíos aleatorios, usar el modelo GLB
        
        if os.path.exists(modelo_path):
            npc["modelo"] = self.loader.loadModel(modelo_path)
            if oponente == "kitty" and os.path.exists("models/amiga.jpg"): # Si es kitty y hay una textura amiga.jpg
                textura = self.loader.loadTexture("models/amiga.jpg")
                npc["modelo"].setTexture(textura)
            elif oponente == "kitty": # Si es kitty y no hay textura, simplemente carga el modelo.
                pass 
        else:
            print(f"Modelo {modelo_path} no encontrado, usando modelo por defecto...")
            npc["modelo"] = self.create_simple_box_model()
        
        npc["modelo"].reparentTo(self.render)
        npc["modelo"].setPos(10, 10, 0.5)
        npc["modelo"].setScale(1.5)
        npc["modelo"].setH(-npc["direccion"])
        
        cNode = CollisionNode("opponent")
        cNode.addSolid(CollisionSphere(0, 0, 0.5, 0.8))
        cNodePath = npc["modelo"].attachNewNode(cNode)
        self.cTrav.addCollider(cNodePath, self.pusher)
        self.pusher.addCollider(cNodePath, npc["modelo"])
        
        self.jugadores.append(npc)
        
        self.taskMgr.add(self.mover_oponente_desafio, "mover_desafio")

    def mover_oponente_desafio(self, task):
        for npc in [j for j in self.jugadores if j['activo']]:
            if npc["invulnerable"] > 0:
                npc["invulnerable"] -= globalClock.getDt()
            if random.random() > 0.98:
                npc["direccion"] += random.uniform(-45, 45)
            
            if self.personaje:
                to_player = self.personaje.getPos() - npc["modelo"].getPos()
                to_player.normalize()
                npc["direccion"] = math.degrees(math.atan2(to_player.x, to_player.y))
            
            dx = math.sin(math.radians(npc["direccion"])) * npc["velocidad"] * globalClock.getDt()
            dy = math.cos(math.radians(npc["direccion"])) * npc["velocidad"] * globalClock.getDt()
            
            npc["modelo"].setPos(
                npc["modelo"].getX() + dx,
                npc["modelo"].getY() + dy,
                0.5
            )
            npc["modelo"].setH(-npc["direccion"])
            
        return task.cont

    def empujar(self):
        if self.personaje:
            for npc in [j for j in self.jugadores if j['activo'] and j['invulnerable'] <= 0]:
                distancia = (self.personaje.getPos() - npc["modelo"].getPos()).length()
                if distancia < 2.5:
                    direccion = math.degrees(math.atan2(
                        npc["modelo"].getX() - self.personaje.getX(),
                        npc["modelo"].getY() - self.personaje.getY()))
                    
                    fuerza = 15.0 + random.uniform(-1.0, 1.0)
                    
                    npc["modelo"].setPos(
                        npc["modelo"].getX() + math.sin(math.radians(direccion)) * fuerza,
                        npc["modelo"].getY() + math.cos(math.radians(direccion)) * fuerza,
                        0.5
                    )
                    
                    npc["direccion"] = direccion
                    npc["invulnerable"] = 1.0
                    
                    if self.estado == "desafio":
                        npc["salud"] = max(0, npc["salud"] - 5)
                    else: # Modo normal, se asume que los NPCs tienen salud en general.
                        npc["salud"] = max(0, npc["salud"] - 5) # NPCs en modo normal también pierden salud al ser empujados.

                    
                    if npc["salud"] <= 0:
                        npc["activo"] = False
                        npc["modelo"].hide()
                        self.puntos += 50
                        self.update_ui_juego()
                        if self.estado == "desafio":
                            if npc["tipo"] == "kitty":
                                self.desafios_desbloqueados["kitty"] = True
                                self.desafios_desbloqueados["proprietary"] = True
                                self.guardar_desbloqueos()
                                self.fin_del_desafio(ganador=True)
                            elif npc["tipo"] == "proprietary":
                                self.desafios_desbloqueados["proprietary"] = True
                                self.desafios_desbloqueados["penny"] = True
                                self.guardar_desbloqueos()
                                self.fin_del_desafio(ganador=True)
                            else:
                                self.fin_del_desafio(ganador=True)
                        else: # Modo normal
                            if len([j for j in self.jugadores if j['activo']]) == 0:
                                self.fin_del_juego(ganador=True)
                    else:
                        self.check_npc_boundary(npc)

    def update_desafio(self, task):
        if self.estado == "pausa":
            self.taskMgr.add(self.pause_cpu_task, "pause_cpu_task")
            return task.cont # Si está pausado, no actualiza el desafío.

        self.game_time += globalClock.getDt()
        self.update_ui_juego()
        
        jugadores_activos = len([j for j in self.jugadores if j['activo']])
        if jugadores_activos == 0:
            self.fin_del_desafio(ganador=True)
            return task.done
        
        if self.vidas <= 0:
            self.fin_del_desafio(ganador=False)
            return task.done
        
        return task.cont

    def pause_cpu_task(self, task):
        # Esta tarea no hace nada, simulando pausar la CPU
        return task.cont

    def fin_del_desafio(self, ganador):
        print("Finalizando desafío...")
        self.limpiar_juego()
        self.limpiar_ui()
        self.estado = "fin_desafio"
        
        if ganador:
            mensaje = "¡DESAFÍO COMPLETADO!"
            color = (0, 1, 0, 1)
        else:
            mensaje = "DESAFÍO FALLIDO"
            color = (1, 0, 0, 1)
        
        self.titulo_fin = OnscreenText(
            text=mensaje,
            scale=0.1,
            parent=base.a2dTopCenter,
            fg=color,
            pos=(0, -0.2),
            font=self.fuente)
        
        self.texto_puntos = OnscreenText(
            text=f"Puntos finales: {self.puntos}",
            scale=0.07,
            fg=(1, 1, 1, 1),
            pos=(0, -0.4),
            parent=base.a2dTopCenter,
            font=self.fuente)
        
        self.boton_menu = DirectButton(
            text="Volver al Menú de Desafíos",
            scale=0.06,
            pos=(0, 0, -0.6),
            command=self.crear_menu_desafios,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)

    def mostrar_instrucciones(self):
        print("Mostrando instrucciones...")
        self.limpiar_ui()
        self.estado = "instrucciones"
        
        instrucciones = [
            "INSTRUCCIONES DEL BATTLE ROYALE",
            "",
            "1. Empuja a los otros jugadores fuera del área segura",
            "2. El área se reduce con el tiempo - mantente dentro",
            "3. Usa WASD para moverte y ESPACIO para empujar",
            "4. Cada empujón exitoso te da puntos",
            "5. Si te caes al vacío, pierdes inmediatamente",
            "6. ¡Cuidado! Los NPCs empujan y tienen 50% de probabilidad de quitar vidas, excepto cerca del centro (0,0)",
            "7. Los NPCs también se empujan entre sí",
            "8. ¡El último en pie gana!",
            "",
            "Desafíos:",
            "- Kitty (Cementerio de Software): Enfrenta a Kitty.",
            "- Proprietary (Bliss): Lucha contra Proprietary.",
            "- Aleatorio: Pelea contra un enemigo aleatorio en un stage aleatorio.",
            "",
            "Controles:",
            "WASD - Movimiento",
            "ESPACIO - Empujar",
            "ESC/P - Pausar",
        ]
        
        self.titulo_instrucciones = OnscreenText(
            text="\n".join(instrucciones),
            scale=0.05,
            parent=base.a2dTopCenter,
            fg=(1, 1, 1, 1),
            pos=(0, -0.1),
            align=TextNode.ACenter,
            font=self.fuente)
        
        self.boton_atras = DirectButton(
            text="Volver",
            scale=0.06,
            pos=(0, 0, -0.8),
            command=self.crear_menu,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)

    def mostrar_creditos(self):
        print("Creando créditos...")
        self.limpiar_ui()
        self.estado = "creditos"
        
        creditos = [
            "CRÉDITOS",
            "",
            "mystery dev: codee and superpropietary",
            "ZAQraven99: konqi",
            "Minibjorn: puffy",
            "stkrudy85: penny",
            "Alessandro Bottura: música del menú",
            "NickisDoge: xenia",
            "Sunspire Studios: Tux",
            "CrystalDaEevee & Typhon306: mozilla",
            "Zi Ye: sinbad and kitty"
        ]
        
        self.titulo_creditos = OnscreenText(
            text="\n\n".join(creditos),
            scale=0.05,
            parent=base.a2dTopCenter,
            fg=(1, 1, 1, 1),
            pos=(0, -0.1),
            align=TextNode.ACenter,
            font=self.fuente)
        
        self.boton_atras = DirectButton(
            text="Volver",
            scale=0.06,
            pos=(0, 0, -0.8),
            command=self.crear_menu,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)

    def ir_a_seleccion(self):
        print("Yendo a selección de personajes...")
        self.limpiar_ui()
        self.crear_seleccion_personajes()

    def crear_seleccion_personajes(self, callback=None):
        print("Creando selección de personajes...")
        self.limpiar_ui()
        self.estado = "seleccion_personaje"
        self.callback_despues_personaje = callback # Para saber qué hacer después de seleccionar personaje

        self.titulo_seleccion = OnscreenText(
            text="Elige tu personaje",
            scale=0.07,
            parent=base.a2dTopCenter,
            fg=(1, 1, 1, 1),
            pos=(0, -0.1),
            font=self.fuente)
        
        personajes = [
            {"nombre": "Godette and Godot", "modelo": "duog", "color": (0.9, 0.6, 0.2, 0.7)},
            {"nombre": "Freedo", "modelo": "freedo", "color": (1.0, 1.0, 1.0, 1.0)},
            {"nombre": "Tux", "modelo": "tud", "color": (0.2, 0.4, 1, 0.7)},
            {"nombre": "Xenia", "modelo": "senia", "color": (0.95, 0.65, 0.1, 1.0)},
            {"nombre": "Mozilla", "modelo": "mozallera", "color": (1.0, 0.5, 0.0, 0.8)},
            {"nombre": "GNU", "modelo": "pirf", "color": (0.8, 0.8, 0, 0.7)},
            {"nombre": "Xue", "modelo": "xue", "color": (0.8, 0.2, 0.5, 1.0)},
            {"nombre": "Duke", "modelo": "dike", "color": (0.5, 0, 0, 0.7)},
            {"nombre": "Puffy", "modelo": "puffy3", "color": (0.5, 0.5, 1, 0.7)},
            {"nombre": "Penny", "modelo": "pennyt", "color": (0.6, 0.8, 0, 0.7)} if self.desafios_desbloqueados["penny"] else None,
            {"nombre": "Adiumy", "modelo": "adium", "color": (0.2, 0.8, 0.2, 0.7)},
            {"nombre": "Purple Pidgin", "modelo": "pidgin", "color": (0.2, 0.8, 0.2, 0.7)},
            {"nombre": "Big Buck Bunny and Frankie", "modelo": "bbbfr", "color": (1.0, 1.0, 1.0, 0.8)},
            {"nombre": "Konqi", "modelo": "kongi", "color": (0, 0.6, 0.8, 0.7)},
            {"nombre": "Blinky", "modelo": "blinky", "color": (0.0, 0.7, 0.3, 0.7)},
            {"nombre": "Bugdroid", "modelo": "droida", "color": (0.3, 0.8, 0.3, 0.7)},
            {"nombre": "Kodee", "modelo": "codee", "color": (0.4, 0.8, 0.3, 0.7)},
            {"nombre": "Buggie", "modelo": "buggie", "color": (0.2, 0.8, 0.5, 1.0)},
            {"nombre": "Puppy Linux", "modelo": "puppyternu", "color": (0.6, 0.2, 0.8, 0.7)},
            {"nombre": "Propietary", "modelo": "propietar", "color": (1, 0, 0, 0.7)} if self.desafios_desbloqueados["proprietary"] else None,
            {"nombre": "Mini Tux", "modelo": "mint", "color": (0.2, 0.2, 0.2, 1.0)},
            {"nombre": "Sinbad", "modelo": "sinbody", "color": (0.5, 0.3, 0.1, 0.7)},
            {"nombre": "Beastie", "modelo": "chuc", "color": (1.0, 1.0, 1.0, 1.0)},
            {"nombre": "Emule", "modelo": "arf", "color": (1, 0.2, 0.8, 0.9)},
            {"nombre": "Wilber", "modelo": "wilber3", "color": (1, 0, 0, 1)},
            {"nombre": "Pepper", "modelo": "peee", "color": (1, 0, 0, 1)},
            {"nombre": "Kitty", "modelo": "kitty1", "color": (0.9, 0.3, 0.3, 1.0)} if self.desafios_desbloqueados["kitty"] else None,
            {"nombre": "Nolok", "modelo": "nolok", "color": (0.2, 0.8, 0.2, 0.7)},
            {"nombre": "Qwen", "modelo": "qwen", "color": (0.2, 0.8, 0.2, 0.7)},
            {"nombre": "Geeko", "modelo": "geeko", "color": (0.2, 0.8, 0.2, 0.7)}
        ]
        personajes = [p for p in personajes if p]
        
        self.botones_personajes = []
        num_personajes = len(personajes)
        # Ajustar el espaciado para que quepan en la pantalla
        cols = 5
        rows = math.ceil(num_personajes / cols)
        
        button_width = 0.2  # Ancho aproximado del botón
        button_height = 0.1 # Alto aproximado del botón
        
        start_x = -0.8
        start_y = -0.2
        x_spacing = 0.4
        y_spacing = 0.15

        for i, p in enumerate(personajes):
            col = i % cols
            row = i // cols
            pos_x = start_x + col * x_spacing
            pos_y = start_y - row * y_spacing
            
            btn = DirectButton(
                text=p["nombre"],
                scale=0.04, # Reducir escala para más botones
                pos=(pos_x, 0, pos_y),
                command=lambda m=p["modelo"]: self.seleccionar_personaje(m),
                frameColor=p["color"],
                text_font=self.fuente)
            btn.setTransparency(TransparencyAttrib.MAlpha)
            btn.bind(DGG.ENTER, self.show_large_model, extraArgs=[p["modelo"]])
            btn.bind(DGG.EXIT, self.hide_large_model)
            self.botones_personajes.append(btn)
        
        self.boton_atras = DirectButton(
            text="Atrás",
            scale=0.05,
            pos=(0, 0, -0.9), # Mover más abajo
            command=self.crear_menu,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)
        
        self.taskMgr.add(self.rotar_modelos, "rotar_modelos")

    def show_large_model(self, modelo, event):
        print(f"Mostrando modelo grande: {modelo}")
        if self.selected_model:
            self.selected_model.removeNode()
        modelo_path = f"models/{modelo}.glb"
        if os.path.exists(modelo_path):
            self.selected_model = self.loader.loadModel(modelo_path)
            self.selected_model.setPos(0, 10, -0.6)  # Ajustado para mejor visibilidad
            self.selected_model.setScale(1.5)
            self.selected_model.setZ(1.0)
            self.selected_model.reparentTo(self.aspect2d)

    def hide_large_model(self, event):
        print("Ocultando modelo grande...")
        if self.selected_model:
            self.selected_model.removeNode()
            self.selected_model = None

    def rotar_modelos(self, task):
        self.rotacion_personaje = (self.rotacion_personaje + 1) % 360
        if self.selected_model:
            self.selected_model.setH(self.rotacion_personaje)
        return task.cont

    def seleccionar_personaje(self, modelo_personaje):
        print(f"Personaje seleccionado: {modelo_personaje}")
        self.personaje_seleccionado = modelo_personaje
        if self.callback_despues_personaje:
            self.callback_despues_personaje()
            self.callback_despues_personaje = None # Resetear el callback
        else:
            self.crear_seleccion_stages()

    def crear_seleccion_stages(self, callback=None):
        print("Creando selección de stages...")
        self.limpiar_ui()
        self.estado = "seleccion_stage"
        self.callback_despues_stage = callback # Para saber qué hacer después de seleccionar stage

        self.titulo_seleccion = OnscreenText(
            text="Elige tu escenario",
            scale=0.07,
            parent=base.a2dTopCenter,
            fg=(1, 1, 1, 1),
            pos=(0, -0.1),
            font=self.fuente)
        
        stages = [
            {"nombre": "Pico Libre", "modelo": "picolibre1.glb", "pos": (-0.6, 0, -0.3), "color": (0.8, 0.2, 0.2, 0.7)},
            {"nombre": "Antártida", "modelo": "antartica.glb", "pos": (-0.2, 0, -0.3), "color": (0.2, 0.4, 0.8, 0.7)},
            {"nombre": "Bliss", "modelo": "box.egg", "pos": (0.2, 0, -0.3), "color": (0.2, 0.8, 0.2, 0.7)},
            {"nombre": "Cementerio de Software", "modelo": "cementerio1.glb", "pos": (0.6, 0, -0.3), "color": (0.5, 0.5, 0.8, 0.7)}
        ]
        
        self.botones_stages = []
        
        for stage in stages:
            btn = DirectButton(
                text=stage["nombre"],
                scale=0.07,
                pos=stage["pos"],
                command=lambda s=stage["modelo"]: self.seleccionar_stage(s),
                frameColor=stage["color"],
                text_font=self.fuente)
            btn.setTransparency(TransparencyAttrib.MAlpha)
            self.botones_stages.append(btn)
        
        self.boton_atras = DirectButton(
            text="Atrás",
            scale=0.05,
            pos=(0, 0, -0.8),
            command=self.crear_seleccion_personajes,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)

    def seleccionar_stage(self, stage_modelo):
        print(f"Stage seleccionado: {stage_modelo}")
        self.stage_seleccionado = stage_modelo
        if self.callback_despues_stage:
            self.callback_despues_stage()
            self.callback_despues_stage = None
        else:
            self.iniciar_juego()

    def iniciar_juego(self):
        print("Iniciando juego normal...")
        self.limpiar_ui()
        self.estado = "jugando"
        self.game_time = 0
        self.vidas = 3
        self.puntos = 0
        self.arena_size = 50
        self.update_safe_zone()
        
        # Cargar skybox
        print("Cargando skybox...")
        if self.skybox:
            self.skybox.removeNode()
        skybox_path = None
        if self.stage_seleccionado in ["picolibre1.glb", "box.egg"]:
            skybox_path = "models/sky1.egg"
        elif self.stage_seleccionado == "antartica.glb":
            skybox_path = "models/sky2.egg"
        elif self.stage_seleccionado == "cementerio1.glb":
            skybox_path = "models/sky3.egg"
        
        if skybox_path and os.path.exists(skybox_path):
            print(f"Cargando skybox: {skybox_path}")
            self.skybox = self.loader.loadModel(skybox_path)
            self.skybox.setScale(100)
            self.skybox.reparentTo(self.render)
            self.skybox.setPos(0, 0, 0)
            self.skybox.setBin("background", 0)
            self.skybox.setDepthWrite(False)
            self.skybox.setTwoSided(True)
        else:
            print(f"Skybox {skybox_path} no encontrado.")
        
        try:
            print("Cargando música del juego...")
            if self.musica:
                self.musica.stop()
            if self.stage_seleccionado == "picolibre1.glb" and os.path.exists("models/tk2.ogg"):
                self.musica = self.loader.loadMusic("models/tk2.ogg")
            elif self.stage_seleccionado == "antartica.glb" and os.path.exists("models/chipdisko.ogg"):
                self.musica = self.loader.loadMusic("models/chipdisko.ogg")
            elif self.stage_seleccionado == "cementerio1.glb" and os.path.exists("models/tk5a.ogg"):
                self.musica = self.loader.loadMusic("models/tk5a.ogg")
            elif os.path.exists("models/music.ogg"):
                self.musica = self.loader.loadMusic("models/music.ogg")
            if self.musica:
                self.musica.setLoop(True)
                self.musica.play()
        except Exception as e:
            print(f"Error cargando música del juego: {str(e)}")
            
        modelo_path = f"models/{self.personaje_seleccionado}.glb"
        if os.path.exists(modelo_path):
            print(f"Cargando personaje: {modelo_path}")
            self.personaje = self.loader.loadModel(modelo_path)
            self.personaje.reparentTo(self.render)
            self.personaje.setPos(0, 0, 0.5)
            self.personaje.setScale(1.2)
            
            cNode = CollisionNode("player")
            cNode.addSolid(CollisionSphere(0, 0, 0.5, 0.8))
            cNodePath = self.personaje.attachNewNode(cNode)
            self.cTrav.addCollider(cNodePath, self.pusher)
            self.pusher.addCollider(cNodePath, self.personaje)
            
            self.camera.setPos(self.personaje.getX(), self.personaje.getY() - 15, 3)
            self.camera.lookAt(self.personaje)
            self.taskMgr.add(self.update_camera, "update_camera")
            
            self.crear_npcs()
            
            self.crear_ui_juego()
            
            self.accept("w", self.mover_adelante)
            self.accept("a", self.mover_izquierda)
            self.accept("s", self.mover_atras)
            self.accept("d", self.mover_derecha)
            self.accept("space", self.empujar)
            self.accept("escape", self.toggle_pausa)
            self.accept("p", self.toggle_pausa)
            
            self.taskMgr.add(self.update_game, "update_game")
            self.taskMgr.add(self.check_boundaries, "check_boundaries")
            self.taskMgr.add(self.shrink_arena, "shrink_arena")
            self.taskMgr.add(self.npc_push_task, "npc_push")

        else:
            print(f"Error: Modelo del personaje {modelo_path} no encontrado.")
            self.fin_del_juego(ganador=False)

    def update_camera(self, task):
        if self.personaje:
            target_x = self.personaje.getX()
            target_y = self.personaje.getY() - 15
            target_z = 3
            
            current_x = self.camera.getX()
            current_y = self.camera.getY()
            current_z = self.camera.getZ()
            
            smooth_factor = 0.1
            new_x = current_x + (target_x - current_x) * smooth_factor
            new_y = current_y + (target_y - current_y) * smooth_factor
            new_z = current_z + (target_z - current_z) * smooth_factor
            
            self.camera.setPos(new_x, new_y, new_z)
            self.camera.lookAt(self.personaje)
            
        return task.cont

    def crear_ui_juego(self):
        print("Creando UI del juego...")
        self.ui_vidas = OnscreenText(
            text=f"Vidas: {self.vidas}",
            scale=0.06,
            parent=base.a2dTopLeft,
            fg=(1, 1, 1, 1),
            pos=(0.1, -0.1),
            font=self.fuente)
        
        self.ui_puntos = OnscreenText(
            text=f"Puntos: {self.puntos}",
            scale=0.06,
            parent=base.a2dTopRight,
            fg=(1, 1, 1, 1),
            pos=(-0.1, -0.1),
            font=self.fuente)
        
        self.ui_tiempo = OnscreenText(
            text=f"Tiempo: {int(self.game_duration - self.game_time)}",
            scale=0.06,
            parent=base.a2dTopCenter,
            fg=(1, 1, 1, 1),
            pos=(0, -0.1),
            font=self.fuente)
            
        self.ui_jugadores = OnscreenText(
            text=f"Jugadores: {len(self.jugadores) + 1}",
            scale=0.06,
            parent=base.a2dBottomCenter,
            fg=(1, 1, 1, 1),
            pos=(0, 0.1),
            font=self.fuente)
            
        self.ui_zona = OnscreenText(
            text=f"Zona segura: {int(self.arena_size)}m",
            scale=0.06,
            parent=base.a2dBottomLeft,
            fg=(1, 1, 1, 1),
            pos=(0.1, 0.1),
            font=self.fuente)

    def update_ui_juego(self):
        # Evitar AttributeError verificando si los objetos existen antes de acceder a ellos
        if hasattr(self, 'ui_vidas') and self.ui_vidas:
            self.ui_vidas.setText(f"Vidas: {self.vidas}")
        if hasattr(self, 'ui_puntos') and self.ui_puntos:
            self.ui_puntos.setText(f"Puntos: {self.puntos}")
        if hasattr(self, 'ui_tiempo') and self.ui_tiempo:
            self.ui_tiempo.setText(f"Tiempo: {max(0, int(self.game_duration - self.game_time))}")
        if hasattr(self, 'ui_jugadores') and self.ui_jugadores:
            # En modo desafío, solo el oponente es un "jugador" aparte del personaje.
            # En modo normal, son todos los NPCs activos + el jugador.
            if self.estado == "desafio":
                active_npcs_count = len([j for j in self.jugadores if j['activo']])
                self.ui_jugadores.setText(f"Oponentes restantes: {active_npcs_count}")
            else:
                self.ui_jugadores.setText(f"Jugadores: {len([j for j in self.jugadores if j['activo']]) + 1}")
        if hasattr(self, 'ui_zona') and self.ui_zona:
            self.ui_zona.setText(f"Zona segura: {int(self.arena_size)}m")

    def crear_npcs(self):
        print("Creando NPCs...")
        modelos_disponibles = ["tud", "freedo", "pennyt", "adium", "kongi", "droida", "chuc", "senia", "mint", "xue", "buggie", "pirf", "dika", 
                               "propietar", "wilber3", "codee", "bbbfr", "mozallera", "sinbody", "puffy3", "peee", "arf", "duog", "kitty1"]
        modelos_disponibles = [m for m in modelos_disponibles if os.path.exists(f"models/{m}.glb")]
        
        if not modelos_disponibles:
            print("Advertencia: No se encontraron modelos GLB para NPCs. Los NPCs no serán cargados.")
            return

        for i in range(self.max_jugadores - 1):
            modelo_npc = random.choice(modelos_disponibles)
            print(f"Cargando NPC: {modelo_npc}")
            npc = {
                "modelo": self.loader.loadModel(f"models/{modelo_npc}.glb"),
                "velocidad": random.uniform(0.5, 2.0),
                "direccion": random.uniform(0, 360),
                "fuerza": random.uniform(1.0, 3.0),
                "activo": True,
                "invulnerable": 0,
                "push_timer": random.uniform(1.0, 3.0),
                "salud": 10 # NPCs en modo normal también tienen salud
            }
            
            npc["modelo"].reparentTo(self.render)
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.arena_size * 0.8)
            npc["modelo"].setPos(
                math.sin(angle) * distance,
                math.cos(angle) * distance,
                0.5
            )
            npc["modelo"].setH(-npc["direccion"])
            
            cNode = CollisionNode(f"npc_{i}")
            cNode.addSolid(CollisionSphere(0, 0, 0.5, 0.8))
            cNodePath = npc["modelo"].attachNewNode(cNode)
            self.cTrav.addCollider(cNodePath, self.pusher)
            self.pusher.addCollider(cNodePath, npc["modelo"])
            
            self.jugadores.append(npc)
            
        self.taskMgr.add(self.mover_npcs, "mover_npcs")

    def mover_npcs(self, task):
        for npc in [j for j in self.jugadores if j['activo']]:
            if npc["invulnerable"] > 0:
                npc["invulnerable"] -= globalClock.getDt()
            
            if random.random() > 0.98:
                npc["direccion"] += random.uniform(-45, 45)
            
            if self.arena_size < 20:
                to_center = Vec3(0, 0, 0) - npc["modelo"].getPos()
                to_center.normalize()
                npc["direccion"] = math.degrees(math.atan2(to_center.x, to_center.y))
            
            dx = math.sin(math.radians(npc["direccion"])) * npc["velocidad"] * globalClock.getDt()
            dy = math.cos(math.radians(npc["direccion"])) * npc["velocidad"] * globalClock.getDt()
            
            npc["modelo"].setPos(
                npc["modelo"].getX() + dx,
                npc["modelo"].getY() + dy,
                0.5
            )
            npc["modelo"].setH(-npc["direccion"])
            
        return task.cont

    def npc_push_task(self, task):
        if self.personaje and self.estado in ["jugando", "desafio"]:
            active_npcs = [j for j in self.jugadores if j['activo'] and j['invulnerable'] <= 0]
            for npc in active_npcs:
                npc["push_timer"] -= globalClock.getDt()
                if npc["push_timer"] <= 0:
                    npc_pos = npc["modelo"].getPos()
                    distance_to_center = math.sqrt(npc_pos.x**2 + npc_pos.y**2)
                    if distance_to_center > 2.0:
                        distancia = (self.personaje.getPos() - npc["modelo"].getPos()).length()
                        if distancia < 2.5:
                            # 50% de probabilidad de quitar vidas
                            if random.random() < 0.5:
                                direccion = math.degrees(math.atan2(
                                    self.personaje.getX() - npc["modelo"].getX(),
                                    self.personaje.getY() - npc["modelo"].getY()))
                                
                                fuerza = npc["fuerza"] * 10.0
                                
                                self.personaje.setPos(
                                    self.personaje.getX() + math.sin(math.radians(direccion)) * fuerza,
                                    self.personaje.getY() + math.cos(math.radians(direccion)) * fuerza,
                                    0.5
                                )
                                
                                self.vidas = max(0, self.vidas - 1)
                                self.update_ui_juego()
                                
                                if self.vidas <= 0:
                                    if self.estado == "desafio":
                                        self.fin_del_desafio(ganador=False)
                                    else:
                                        self.fin_del_juego(ganador=False)
                                    return task.done
                        
                        for other_npc in [j for j in active_npcs if j != npc]:
                            distancia_npc = (npc["modelo"].getPos() - other_npc["modelo"].getPos()).length()
                            if distancia_npc < 2.5:
                                direccion = math.degrees(math.atan2(
                                    other_npc["modelo"].getX() - npc["modelo"].getX(),
                                    other_npc["modelo"].getY() - npc["modelo"].getY()))
                                
                                fuerza = npc["fuerza"] * 10.0
                                
                                other_npc["modelo"].setPos(
                                    other_npc["modelo"].getX() + math.sin(math.radians(direccion)) * fuerza,
                                    other_npc["modelo"].getY() + math.cos(math.radians(direccion)) * fuerza,
                                    0.5
                                )
                                
                                other_npc["direccion"] = direccion
                                other_npc["invulnerable"] = 1.0
                                
                                self.check_npc_boundary(other_npc)
                                
                    npc["push_timer"] = random.uniform(1.0, 3.0)
        return task.cont

    def check_npc_boundary(self, npc):
        pos = npc["modelo"].getPos()
        distance = math.sqrt(pos.x**2 + pos.y**2)
        
        if distance > self.arena_size:
            npc["activo"] = False
            npc["modelo"].hide()
            self.puntos += 10
            self.update_ui_juego()

    def check_boundaries(self, task):
        if self.personaje:
            pos = self.personaje.getPos()
            distance = math.sqrt(pos.x**2 + pos.y**2)
            
            if distance > self.arena_size:
                self.vidas = 0
                self.update_ui_juego()
                if self.estado == "desafio":
                    self.fin_del_desafio(ganador=False)
                else:
                    self.fin_del_juego(ganador=False)
        
        return task.cont

    def shrink_arena(self, task):
        self.shrink_timer += globalClock.getDt()
        
        if self.shrink_timer >= self.shrink_interval and self.arena_size > 10:
            self.shrink_timer = 0
            self.arena_size = max(10, self.arena_size - 5)
            self.update_safe_zone()
            self.update_ui_juego()
            
        return task.cont

    def update_game(self, task):
        if self.estado == "pausa":
            return task.cont

        self.game_time += globalClock.getDt()
        self.update_ui_juego()
        
        jugadores_activos = len([j for j in self.jugadores if j['activo']])
        if jugadores_activos == 0:
            self.fin_del_juego(ganador=True)
            return task.done
        
        if self.game_time >= self.game_duration:
            self.fin_del_juego(ganador=jugadores_activos == 0) # Si quedan jugadores y el tiempo se acaba, no ganas.
            return task.done

        return task.cont

    def fin_del_juego(self, ganador):
        print("Finalizando juego normal...")
        self.limpiar_juego()
        self.limpiar_ui()
        self.estado = "fin_juego"
        
        if ganador:
            mensaje = "¡HAS GANADO!"
            color = (0, 1, 0, 1)
        else:
            mensaje = "JUEGO TERMINADO"
            color = (1, 0, 0, 1)
        
        self.titulo_fin = OnscreenText(
            text=mensaje,
            scale=0.1,
            parent=base.a2dTopCenter,
            fg=color,
            pos=(0, -0.2),
            font=self.fuente)
        
        self.texto_puntos = OnscreenText(
            text=f"Puntos finales: {self.puntos}",
            scale=0.07,
            parent=base.a2dTopCenter,
            fg=(1, 1, 1, 1),
            pos=(0, -0.4),
            font=self.fuente)
        
        self.boton_menu = DirectButton(
            text="Volver al menú",
            scale=0.06,
            pos=(0, 0, -0.6),
            command=self.volver_al_menu,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)

    def mover_adelante(self):
        if self.personaje and self.estado in ["jugando", "desafio"]:
            self.personaje.setY(self.personaje, 3.0 * globalClock.getDt())

    def mover_atras(self):
        if self.personaje and self.estado in ["jugando", "desafio"]:
            self.personaje.setY(self.personaje, -3.0 * globalClock.getDt())

    def mover_izquierda(self):
        if self.personaje and self.estado in ["jugando", "desafio"]:
            self.personaje.setX(self.personaje, -3.0 * globalClock.getDt())

    def mover_derecha(self):
        if self.personaje and self.estado in ["jugando", "desafio"]:
            self.personaje.setX(self.personaje, 3.0 * globalClock.getDt())

    def limpiar_ui(self):
        print("Limpiando UI...")
        ui_elements = [
            "titulo", "boton_jugar", "boton_salir", "boton_instrucciones", "boton_creditos",
            "titulo_seleccion", "boton_atras", "botones_stages",
            "titulo_instrucciones",
            "titulo_creditos",
            "titulo_fin", "texto_puntos", "boton_menu",
            "ui_vidas", "ui_puntos", "ui_tiempo", "ui_jugadores", "ui_zona",
            "titulo_pausa", "boton_reanudar", "boton_menu_principal", "boton_salir_pausa",
            "boton_desafios", "titulo_desafios", "boton_desafio_kitty", "boton_desafio_proprietary", "boton_desafio_aleatorio",
        ]
        
        for attr in ui_elements:
            if hasattr(self, attr):
                element = getattr(self, attr)
                if element is not None:
                    if isinstance(element, list):
                        for item in element:
                            if hasattr(item, 'destroy'):
                                item.destroy()
                    elif hasattr(element, 'destroy'):
                        element.destroy()
                    setattr(self, attr, None)
            
        if hasattr(self, 'botones_personajes'):
            for btn in self.botones_personajes:
                if hasattr(btn, 'destroy'):
                    btn.destroy()
            self.botones_personajes = []
                
        if hasattr(self, 'selected_model') and self.selected_model:
            self.selected_model.removeNode()
            self.selected_model = None

    def limpiar_juego(self):
        print("Limpiando juego...")
        if self.personaje:
            self.personaje.removeNode()
            self.personaje = None
            
        for npc in self.jugadores:
            if "modelo" in npc and npc["modelo"] is not None:
                npc["modelo"].removeNode()
        self.jugadores = []
            
        if self.safe_zone:
            self.safe_zone.removeNode()
            self.safe_zone = None
            
        if self.skybox:
            self.skybox.removeNode()
            self.skybox = None
            
        self.taskMgr.remove("mover_npcs")
        self.taskMgr.remove("update_game")
        self.taskMgr.remove("update_desafio")
        self.taskMgr.remove("check_boundaries")
        self.taskMgr.remove("shrink_arena")
        self.taskMgr.remove("update_camera")
        self.taskMgr.remove("rotar_modelos")
        self.taskMgr.remove("npc_push")
        self.taskMgr.remove("mover_desafio")
        self.taskMgr.remove("pause_cpu_task")

        if self.musica:
            self.musica.stop()
            self.musica = None

    def volver_a_seleccion(self):
        print("Volviendo a selección de personajes...")
        self.limpiar_juego()
        self.limpiar_ui()
        self.crear_seleccion_personajes()
        try:
            if os.path.exists("models/music.ogg"):
                if self.musica:
                    self.musica.stop()
                self.musica = self.loader.loadMusic("models/music.ogg")
                self.musica.setLoop(True)
                self.musica.play()
        except Exception as e:
            print(f"Error cargando música del menú: {str(e)}")

    def volver_al_menu(self):
        print("Volviendo al menú principal...")
        self.limpiar_ui()
        self.limpiar_juego()
        self.crear_menu()

    def salir_juego(self):
        print("Saliendo del juego...")
        try:
            if self.musica:
                self.musica.stop()
            self.limpiar_juego()
            self.limpiar_ui()
            self.ignoreAll()
            base.userExit()
        except Exception as e:
            print(f"Error al salir del juego: {str(e)}")
            sys.exit(1)

    def toggle_pausa(self):
        print("Toggling pausa...")
        if self.estado in ["jugando", "desafio"]:
            self.estado_anterior = self.estado # Guardar el estado actual
            self.estado = "pausa"
            
            # Pausar todas las tareas del juego/desafío
            for task_name in ["update_game", "update_desafio", "mover_npcs", "mover_desafio", 
                              "check_boundaries", "shrink_arena", "update_camera", "npc_push"]:
                self.taskMgr.remove(task_name)
            
            # Pausar la CPU en el modo desafío
            if self.estado_anterior == "desafio":
                self.taskMgr.add(self.pause_cpu_task, "pause_cpu_task")

            # Reducir volumen de la música
            if self.musica:
                self.musica.setVolume(0.1)

            # Mostrar menú de pausa
            self.crear_menu_pausa()
            self.ignoreAll() # Ignorar controles de juego
            self.accept("escape", self.toggle_pausa)
            self.accept("p", self.toggle_pausa)
            
        elif self.estado == "pausa":
            self.estado = self.estado_anterior # Restaurar el estado anterior
            
            # Reanudar tareas según el estado anterior
            if self.estado == "jugando":
                self.taskMgr.add(self.update_game, "update_game")
                self.taskMgr.add(self.mover_npcs, "mover_npcs")
                self.taskMgr.add(self.shrink_arena, "shrink_arena")
                self.taskMgr.add(self.npc_push_task, "npc_push")

            elif self.estado == "desafio":
                self.taskMgr.add(self.update_desafio, "update_desafio")
                self.taskMgr.add(self.mover_oponente_desafio, "mover_desafio")
            
            # Tareas comunes
            self.taskMgr.add(self.check_boundaries, "check_boundaries")
            self.taskMgr.add(self.update_camera, "update_camera")
            self.taskMgr.remove("pause_cpu_task") # Asegurarse de eliminar la tarea de pausa de CPU

            # Restaurar volumen de la música
            if self.musica:
                self.musica.setVolume(1.0)

            self.limpiar_ui() # Limpiar menú de pausa
            
            # Restaurar controles de juego
            self.accept("w", self.mover_adelante)
            self.accept("a", self.mover_izquierda)
            self.accept("s", self.mover_atras)
            self.accept("d", self.mover_derecha)
            self.accept("space", self.empujar)
            self.accept("escape", self.toggle_pausa)
            self.accept("p", self.toggle_pausa)

    def crear_menu_pausa(self):
        print("Creando menú de pausa...")
        self.titulo_pausa = OnscreenText(
            text="PAUSA",
            scale=0.1,
            parent=base.a2dTopCenter,
            fg=(1, 0.5, 0, 1),
            pos=(0, -0.2),
            font=self.fuente)
        
        self.boton_reanudar = DirectButton(
            text="Reanudar",
            scale=0.06,
            pos=(0, 0, -0.4),
            command=self.toggle_pausa,
            frameColor=(0, 0.6, 0, 0.7),
            text_font=self.fuente)
        
        self.boton_menu_principal = DirectButton(
            text="Menú Principal",
            scale=0.06,
            pos=(0, 0, -0.55),
            command=self.volver_al_menu,
            frameColor=(0.5, 0.5, 0.5, 0.7),
            text_font=self.fuente)
        
        self.boton_salir_pausa = DirectButton(
            text="Salir",
            scale=0.06,
            pos=(0, 0, -0.7),
            command=self.salir_juego,
            frameColor=(0.8, 0, 0, 0.7),
            text_font=self.fuente)

if __name__ == "__main__":
    game = SupertuxBattleRoyale()
    game.run()