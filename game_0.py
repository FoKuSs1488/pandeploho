# pip install panda3d

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties
from panda3d.core import CollisionNode, CollisionSphere, CollisionBox, Point3, CollisionPlane, Plane, Vec3, CollisionTraverser, CollisionHandlerPusher
from panda3d.core import AmbientLight, DirectionalLight, PointLight, Spotlight, PerspectiveLens, Vec4
import math

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #  Завантаження моделей
        self.player = loader.loadModel('models/panda')
        self.player.reparentTo(render)
        self.player.setPos(50, 50, 1)
        self.player.setScale(0.7)

        self.model_cafe = loader.loadModel('models/Cafeteria/Cafeteria')
        self.model_cafe.setScale(0.07)
        self.model_cafe.reparentTo(render)
        self.model_cafe.setPos(0, 0, 10)
        self.model_cafe.setH(self.model_cafe.getH() - 20)

        self.sky = loader.loadModel('models/PeachSky/PeachSky')
        self.sky.reparentTo(render)

        self.big_table = loader.loadModel('models/BigTable/BigTable')
        self.big_table.reparentTo(render)
        self.big_table.setScale(2)
        self.big_table.setPos(10, 100, 0)

        self.counter = loader.loadModel('models/Counter/Counter')
        self.counter.reparentTo(render)
        self.counter.setScale(2)
        self.counter.setPos(100, 10, 0)

        # 1️⃣ Створюємо менеджер колізій
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # 2️⃣ Колізія для великого столу
        big_table_min_pt, big_table_max_pt = self.big_table.getTightBounds()
        print(big_table_min_pt, big_table_max_pt)
        big_table_solid = CollisionBox(big_table_min_pt, big_table_max_pt)
        big_table_node = CollisionNode('big_table')
        big_table_node.addSolid(big_table_solid)
        big_table_np = render.attachNewNode(big_table_node)
        # Показати бокс (для тесту)
        # big_table_np.show()  # побачити колізію

        # 2️⃣ Колізія для стійки
        counter_min_pt, counter_max_pt = self.counter.getTightBounds()
        # print(big_table_min_pt, big_table_max_pt)
        counter_solid_1 = CollisionBox(counter_min_pt, (counter_min_pt[0] + 6, counter_max_pt[1], counter_max_pt[2]))
        counter_solid_2 = CollisionBox(counter_min_pt, (counter_max_pt[0], counter_min_pt[1] + 6, counter_max_pt[2]))
        counter_node = CollisionNode('counter')
        counter_node.addSolid(counter_solid_1)
        counter_node.addSolid(counter_solid_2)
        counter_np = render.attachNewNode(counter_node)
        # Показати бокс (для тесту)
        # counter_np.show()  # побачити колізію

        # 2️⃣ Колізія для гравця (сфера навколо моделі)
        player_min_pt, player_max_pt = self.player.getTightBounds()
        # print(player_min_pt, player_max_pt)
        radius = player_max_pt.z - player_min_pt.z // 2  # приблизний радіус моделі

        player_solid = CollisionSphere(0, 0, 0 + radius, radius)  # трохи менше для точнос
        player_node = CollisionNode("player")
        player_node.addSolid(player_solid)
        player_nodepath = self.player.attachNewNode(player_node)
        # Щоб бачити колізію (лише для тесту)
        # player_nodepath.show()

        # 4️⃣ Додаємо обробку зіткнень
        self.pusher.addCollider(player_nodepath, self.player)
        self.cTrav.addCollider(player_nodepath, self.pusher)

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
        if self.keys["w"]: self.player.setY(self.player, -speed)
        if self.keys["s"]: self.player.setY(self.player, speed)
        if self.keys["a"]: self.player.setX(self.player, speed)
        if self.keys["d"]: self.player.setX(self.player, -speed)

        #  Оберт гравця спиною до камери
        self.player.setH(self.camera_angle_h + 180) #  задає горизонтальний кут об’єкта (heading)

        #  оберт камери по колу
        px, py, pz = self.player.getPos()
        rad = math.radians(self.camera_angle_h)
        cam_x = px + self.camera_distance * math.sin(rad)
        cam_y = py - self.camera_distance * math.cos(rad)

        self.camera.setPos(cam_x, cam_y, pz + self.camera_height)
        self.camera.lookAt(self.player.getPos() + Point3(0, 0, 10))


        render.setShaderAuto()

        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(0.3, 0.3, 0.4, 1))  # трохи синюватий відтінок — ефект вечора
        ambient_np = render.attachNewNode(ambient)
        render.setLight(ambient_np)

        #  Спрямоване світло (сонце)
        sun = DirectionalLight('sun')
        sun.setColor(Vec4(0.8, 0.7, 0.5, 1))  # теплий жовто-помаранчевий колір, як на заході
        sun_np = render.attachNewNode(sun)
        sun_np.setHpr(45, -45, 0)  # кут променів — зверху під нахилом
        render.setLight(sun_np)

        #  Точкове світло (лампа біля гравця)
        lamp = PointLight('lamp')
        lamp.setColor(Vec4(2, 1.5, 1, 1))  # м’яке тепле світло
        lamp.setAttenuation((1, 0.1, 0.01))  # сила затухання (чим менше друге число — тим ширше світить)
        lamp_np = self.player.attachNewNode(lamp)
        lamp_np.setPos(0, 0, 2)  # трохи вище моделі гравця
        render.setLight(lamp_np)

        #  Прожектор (якщо треба, щоб щось підсвічував)
        spot = Spotlight('spot')
        spot.setColor(Vec4(1, 1, 0.8, 1))  # м’яке біло-жовте світло
        lens = PerspectiveLens()
        lens.setFov(60)  # кут освітлення
        spot.setLens(lens)

        spot_np = render.attachNewNode(spot)
        spot_np.setPos(10, 50, 10)  # позиція прожектора у світі
        spot_np.lookAt(self.counter)  # куди він світить
        render.setLight(spot_np)

        # Створюємо звуковий менеджер
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)

        # Фонова музика
        self.bg_music = loader.loadMusic('sounds/oga_majitapioka.mp3')
        self.bg_music.setLoop(True)
        self.bg_music.play()

        # Звук при дії
        self.washing_sound = loader.loadSfx('sounds/386508-pub_glass_wash_rinse.wav')


        return Task.cont


base = Game()
base.run()
