# pip install panda3d

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
import time

from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties, CollisionTraverser, CollisionHandlerPusher
from panda3d.core import CollisionNode, CollisionSphere, CollisionBox, Point3, CollisionPlane, Plane, Vec3
from direct.showbase import Audio3DManager
from random import randint
import math

from panda3d.core import AmbientLight, DirectionalLight, PointLight, Spotlight, PerspectiveLens, Vec4


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #  Завантаження моделей
        self.player = loader.loadModel('models/panda')
        self.player.setPos(50, 50, 0)
        self.player.setScale(0.7)
        self.player.reparentTo(render)

        self.model_training_gym = loader.loadModel('models/basketball_field/scene.gltf')
        self.model_training_gym.setScale(7)
        self.model_training_gym.reparentTo(render)
        self.model_training_gym.setPos(0, 0, -2)
        self.model_training_gym.setHpr(0, 90, 90)

        self.model_ground = loader.loadModel('models/Ground2/Ground2')
        self.model_ground.setScale(7)
        self.model_ground.reparentTo(render)
        self.model_ground.setPos(0, 0, -2.01)

        self.model_sky = loader.loadModel('models/blue_sky_sphere/blue_sky_sphere')
        self.model_sky.setScale(7)
        self.model_sky.reparentTo(render)


        #  Камера
        self.disableMouse()
        self.camera_distance = 60
        self.camera_height = 20
        self.camera_angle_h = 0

        # Сховати курсор
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        # Щоб камера могла рухатись від миші
        self.center_mouse()

        #  Клавіші
        self.keys = {"w": False, "s": False, "a": False, "d": False}
        for key in self.keys.keys():
            self.accept(key, self.set_key, [key, True])
            self.accept(f"{key}-up", self.set_key, [key, False])

        # Мишка
        self.accept("escape", exit)  # Вихід по ESC
        self.taskMgr.add(self.update, "UpdateTask")
        self.taskMgr.add(self.mouse_update, "MouseTask")

        # Налаштовуємо світло
        # Розсіяне світло
        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(0.5, 0.5, 0.5, 1))  # трохи сірувате світло
        ambient_np = render.attachNewNode(ambient)
        render.setLight(ambient_np)
        # спрямоване світло (сонце)
        sun = DirectionalLight('sun')
        sun.setColor(Vec4(1, 1, 1, 0.1))  # теплий відтінок сонця
        sun_np = render.attachNewNode(sun)
        sun_np.setHpr(20, -70, 0)  # кут падіння світла
        render.setLight(sun_np)


        # Створюємо звуковий менеджер
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)

         #Фонова музика
        self.bg_music = loader.loadMusic('sounds/chiptune-sherlock-holmes-anthem-215252.mp3')
        self.bg_music.setLoop(True)
        self.bg_music.play()

        # Звук при дії
        self.ball_collect_sound = loader.loadSfx('sounds/SMS_-_APChHI_(ringon.site).mp3')

        self.start_time = time.time()
        self.timer_text = OnscreenText(
            text="Time: 0 s",
            pos=(-1, 0.7),
            scale=0.07,
            mayChange=True,
            align=TextNode.ALeft,  # вирівнювання
            fg=(1, 1, 1, 1),  # колір (білий)
        )

        self.taskMgr.add(self.update_timer, "UpdateTimerTask")
        self.balls = []
        self.generate_ball()

        self.keys["e"] = False
        self.accept("e", self.set_key, ["e", True])
        self.accept("e-up", self.set_key, ["e", False])

        self.collect_ball_text = OnscreenText(
            text="20 balls left",
            pos=(-1, 0.5),
            scale=0.07,
            mayChange=True,
            align=TextNode.ALeft,  # вирівнювання
            fg=(1, 1, 1, 1),  # колір (білий)
        )

        self.taskMgr.add(self.collect_ball, "CollectballTask")


    #  Обробка клавіш
    def set_key(self, key, value):
        self.keys[key] = value

    #  Центрування миші
    def center_mouse(self):
        self.win.movePointer(0, int(self.win.getXSize()/2), int(self.win.getYSize()/2))

    #  Рух камери мишкою
    def mouse_update(self, task):
        if self.mouseWatcherNode.hasMouse():
            x = self.win.getPointer(0).getX()
            center_x = self.win.getXSize() / 2

            # Поворот за мишкою
            self.camera_angle_h -= (x - center_x) * 0.2

            # Повернути мишку назад до центру
            self.center_mouse()
        return Task.cont

    #  Ігровий цикл
    def update(self, task):
        speed = 0.5
        #  Рух гравця (WASD)

        print(self.player.getPos())
        if self.keys["w"]: self.player.setY(self.player, -speed)
        if self.keys["s"]: self.player.setY(self.player, speed)
        if self.keys["a"]: self.player.setX(self.player, speed)
        if self.keys["d"]: self.player.setX(self.player, -speed)

        #  Оберт гравця спиною до камери
        self.player.setH(self.camera_angle_h + 180)

        #  оберт камери по колу
        px, py, pz = self.player.getPos()
        rad = math.radians(self.camera_angle_h)
        cam_x = px + self.camera_distance * math.sin(rad)
        cam_y = py - self.camera_distance * math.cos(rad)

        self.camera.setPos(cam_x, cam_y, pz + self.camera_height)
        self.camera.lookAt(self.player.getPos() + Point3(0, 0, 10))

        return Task.cont



    def update_timer(self, task):
        elapsed = int(time.time() - self.start_time)
        self.timer_text.setText(f"Time: {elapsed} c")
        return Task.cont


    def toggle_menu(self):
        """Відкрити/закрити меню"""
        if self.menu_open:
            props = WindowProperties()
            props.setCursorHidden(True)
            self.win.requestProperties(props)
            self.menu_frame.hide()
            self.taskMgr.add(self.mouse_update, "MouseTask")
        else:
            props = WindowProperties()
            props.setCursorHidden(False)
            self.win.requestProperties(props)
            self.menu_frame.show()
            self.taskMgr.remove("MouseTask")
        self.menu_open = not self.menu_open

    # ⬇️⬇️⬇️
    def button_clicked(self, button_number):
        """Подія натискання кнопки"""
        print(f"Button {button_number} is clicked!")

    def generate_ball(self):
        for i in range(20):
            ball = loader.loadModel('models/ball/scene.gltf')
            ball.setPos( randint(-106, 107),randint(-62, 67), 0)
            ball.setScale(0.0175)
            ball.reparentTo(render)
            self.balls.append(ball)

    def collect_ball(self, task):
        # мячік можна зібрати ТІЛЬКИ якщо натиснута клавіша E
        if not self.keys["e"]:
            return Task.cont

        player_pos = self.player.getPos(render)
        for ball in self.balls[:]:
            ball_pos = ball.getPos(render)
            distance = (player_pos - ball_pos).length()
            if distance < 5:
                ball.removeNode()
                self.balls.remove(ball)
                self.ball_collect_sound.play()
                self.collect_ball_text.setText(str(len(self.balls)) + " balls left")
        return Task.cont

base = Game()
base.run()
