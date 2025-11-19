from direct.showbase.ShowBase  import ShowBase
from panda3d.core import WindowProperties
from direct.task import Task
from panda3d.core import WindowProperties
import math



class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.player = loader.loadModel('models/panda')
        self.player.reparentTo(render)
        self.model_cafe = loader.loadModel('models/Cafeteria/Cafeteria')
        self.model_cafe.reparentTo(render)
        self.model_cafe.setScale(0.1)
        self.player.setPos(0, 100, -10)

        base.camLens.setFov(120)

        #КАМЕРА
        self.disableMouse()
        self.camera_distance = 60
        self.camera_height = 20
        self.camera_angle_h = 0

        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

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

        #  Обробка клавіш
    def set_key(self, key, value):
        self.keys[key] = value

        #  Центрування миші
    def center_mouse(self):
        self.win.movePointer(0, int(self.win.getXSize() / 2), int(self.win.getYSize() / 2))

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
        if self.keys["w"]: self.player.setY(self.player, -speed)
        if self.keys["s"]: self.player.setY(self.player, speed)
        if self.keys["a"]: self.player.setX(self.player, speed)
        if self.keys["d"]: self.player.setX(self.player, -speed)

        #  Оберт гравця спиною до камери
        self.player.setH(self.camera_angle_h + 180)  # задає горизонтальний кут об’єкта (heading)

        #  оберт камери по колу
        px, py, pz = self.player.getPos()
        rad = math.radians(self.camera_angle_h)
        cam_x = px + self.camera_distance * math.sin(rad)
        cam_y = py - self.camera_distance * math.cos(rad)

        self.camera.setPos(cam_x, cam_y, pz + self.camera_height)
        self.camera.lookAt(self.player)

        return Task.cont


base = Game()

base.run()

