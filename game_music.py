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

        self.model_training_gym = loader.loadModel('models/training_gym/scene.gltf')
        self.model_training_gym.setScale(7)
        self.model_training_gym.reparentTo(render)
        self.model_training_gym.setPos(0, 0, -2)

        self.model_training_gym.setHpr(0, 90, 90)
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

        # coach = loader.loadModel('models/coatrack2/coatrack2')
        # coach.setH(90)
        # coach.reparentTo(render)
        # coach.setScale(2.3)
        # coach.setPos(80, 10, 0)
        # coach_min_pt, coach_max_pt = coach.getTightBounds()
        # coach_solid = CollisionBox(coach_min_pt, coach_max_pt)
        # coach_node = CollisionNode('coach')
        # coach_node.addSolid(coach_solid)
        # coach_np = render.attachNewNode(coach_node)

        # y = 100
        # for i in range(3):
        #     bookcase = loader.loadModel('models/bookcase/bookcase')
        #     bookcase.setH(90)
        #     bookcase.reparentTo(render)
        #     bookcase.setScale(2.3)
        #     bookcase.setPos(160, y, 0)
        #     bookcase_min_pt, bookcase_max_pt = bookcase.getTightBounds()
        #     bookcase_solid = CollisionBox(bookcase_min_pt, bookcase_max_pt)
        #     bookcase_node = CollisionNode('bookcase')
        #     bookcase_node.addSolid(bookcase_solid)
        #     bookcase_np = render.attachNewNode(bookcase_node)
        #
        #     # Показати бокс (для тесту)
        #     # big_table_np.show()  # побачити колізію
        #     y -= 30



        # --- 📦 КОЛІЗІЇ ---
        # Створюємо менеджер колізій
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # Колізія для великого столу
        big_table_min_pt, big_table_max_pt = self.big_table.getTightBounds()
        big_table_solid = CollisionBox(big_table_min_pt, big_table_max_pt)
        big_table_node = CollisionNode('big_table')
        big_table_node.addSolid(big_table_solid)
        big_table_np = render.attachNewNode(big_table_node)
        # Показати бокс (для тесту)
        # big_table_np.show()  # побачити колізію

        # Колізія для стійки
        counter_min_pt, counter_max_pt = self.counter.getTightBounds()
        counter_solid_1 = CollisionBox(counter_min_pt, (counter_min_pt[0] + 6, counter_max_pt[1], counter_max_pt[2]))
        counter_solid_2 = CollisionBox(counter_min_pt, (counter_max_pt[0], counter_min_pt[1] + 6, counter_max_pt[2]))
        counter_node = CollisionNode('counter')
        counter_node.addSolid(counter_solid_1)
        counter_node.addSolid(counter_solid_2)
        counter_np = render.attachNewNode(counter_node)
        # Показати бокс (для тесту)
        # counter_np.show()  # побачити колізію

        # Колізія для гравця (сфера навколо моделі)
        player_min_pt, player_max_pt = self.player.getTightBounds()
        # print(player_min_pt, player_max_pt)
        radius = player_max_pt.z - player_min_pt.z // 2  # приблизний радіус моделі
        player_solid = CollisionSphere(0, 0, 0 + radius, radius)  # трохи менше для точнос
        player_node = CollisionNode("player")
        player_node.addSolid(player_solid)
        player_nodepath = self.player.attachNewNode(player_node)
        # Щоб бачити колізію (лише для тесту)
        # player_nodepath.show()

        # # Колізія для підлоги
        # min_pt, max_pt = self.model_training_gym.getTightBounds()
        # print(min_pt, max_pt)
        #
        # floor_solid = CollisionBox(Point3(min_pt.x, min_pt.y, min_pt.z - 1), Point3(max_pt.x, max_pt.y, min_pt.z))
        # floor_node = CollisionNode('floor')
        # floor_node.addSolid(floor_solid)
        # floor_np = render.attachNewNode(floor_node)
        # Показати бокс (для тесту)
        # floor_np.show()  # побачити колізію

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
        self.taskMgr.add(self.washing_dishes, "WashingTask")

        # Налаштовуємо світло
        # Розсіяне світло
        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(0.1, 0.1, 0.1, 1))  # трохи сірувате світло
        ambient_np = render.attachNewNode(ambient)
        render.setLight(ambient_np)
        # спрямоване світло (сонце)
        sun = DirectionalLight('sun')
        sun.setColor(Vec4(0.5, 0.5, 0.5, 1))  # теплий відтінок сонця
        sun_np = render.attachNewNode(sun)
        sun_np.setHpr(20, -70, 0)  # кут падіння світла
        render.setLight(sun_np)
        # точкове світло (лампочка)
        lamp = PointLight('lamp')
        lamp.setColor(Vec4(5, 2, 2, 1))  # тепле світло
        lamp_np = self.player.attachNewNode(lamp)
        lamp_np.setPos(0, 0, 0)  # положення лампи
        render.setLight(lamp_np)
        lamp.setAttenuation((1, 0.08, 0))
        # прожектор (світло у формі конуса)
        spot = Spotlight('spot')
        spot.setColor(Vec4(1, 1, 1, 1))
        lens = PerspectiveLens()
        lens.setFov(100)  # ширина конуса освітлення
        spot.setLens(lens)

        spot_np = render.attachNewNode(spot)
        spot_np.setPos(10, 50, 0)
        spot_np.lookAt(self.big_table)  # спрямування на об’єкт
        render.setLight(spot_np)

        # Створюємо звуковий менеджер
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)

        # Фонова музика
        self.bg_music = loader.loadMusic('sounds/oga_majitapioka.mp3')
        self.bg_music.setLoop(True)
        self.bg_music.play()

        # Звук при дії
        self.washing_sound = loader.loadSfx('sounds/386508-pub_glass_wash_rinse.wav')
        # прапорець меню
        self.menu_open = False

        # створюємо фрейм меню (фон меню)
        self.menu_frame = DirectFrame(
            frameColor=(0.5, 0.5, 0.5, 0.7),  # напівпрозорий чорний
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            pos=(0, 0, 0)
        )
        self.menu_frame.hide()  # спочатку меню приховане

        # створюємо 3 кнопки в меню
        self.buttons = []
        for i in range(3):
            btn = DirectButton(
                text=f"Button {i + 1}",
                scale=0.07,
                pos=(0, 0, 0.2 - i * 0.2),
                parent=self.menu_frame,
                command=self.button_clicked,
                extraArgs=[i + 1]
            )
            self.buttons.append(btn)

        # прив’язуємо клавішу M
        self.accept("m", self.toggle_menu)
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

    def washing_dishes(self, task):
        player_pos = self.player.getPos(render)
        counter_pos = self.counter.getPos(render)
        distance = (player_pos - counter_pos).length()
        if distance < 15:
            if self.washing_sound.status() != self.washing_sound.PLAYING:
                self.washing_sound.play()
        else:
            if self.washing_sound.status() == self.washing_sound.PLAYING:
                self.washing_sound.stop()
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
base = Game()
base.run()
