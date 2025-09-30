import kivy
kivy.require('2.0.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Rectangle, Line, RoundedRectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.video import Video
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty
from kivy.utils import platform
import os
import json
from datetime import datetime

# Настройка окна только для desktop
if platform not in ('android', 'ios'):
    Window.size = (375, 667)
Window.clearcolor = (0, 0, 0, 1)


def get_data_dir():
    """Получает правильную директорию для данных в зависимости от платформы"""
    if platform == 'android':
        from android.storage import app_storage_path
        return app_storage_path()
    else:
        return os.path.dirname(os.path.abspath(__file__))


# Пути к ресурсам (относительные)
VIDEO_PATH = os.path.join(get_data_dir(), "z-f.mp4")
CONFIG_FILE = os.path.join(get_data_dir(), "vpn_config.json")


class ConfigDatabase:
    """Класс для работы с конфигурацией VPN"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = self.load_config()
    
    def load_config(self):
        """Загружает конфигурацию из файла"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self, config_string):
        """Сохраняет конфигурацию в файл"""
        try:
            self.config = {
                'config': config_string,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except:
            return False
    
    def has_config(self):
        """Проверяет, есть ли сохраненная конфигурация"""
        return 'config' in self.config and self.config['config']
    
    def get_config(self):
        """Получает сохраненную конфигурацию"""
        return self.config.get('config', '')


class DeadInput(FloatLayout):
    """Красивое поле ввода с закругленными краями"""
    def __init__(self, hint_text='', password=False, multiline=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 50
        
        with self.canvas.before:
            self.border_color = Color(0.3, 0.3, 0.3, 1)
            self.border = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            self.bg_color = Color(0.1, 0.1, 0.1, 0.9)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        
        self.text_input = TextInput(
            hint_text=hint_text,
            hint_text_color=(0.5, 0.5, 0.5, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            background_color=(0, 0, 0, 0),
            cursor_color=(0.8, 0.8, 0.8, 1),
            padding=[15, 12],
            font_size='15sp',
            multiline=multiline,
            password=password,
            size_hint=(0.95, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.text_input)
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        self.text_input.bind(focus=self.on_focus)
    
    def update_graphics(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size
        self.bg.pos = (self.pos[0] + 2, self.pos[1] + 2)
        self.bg.size = (self.size[0] - 4, self.size[1] - 4)
    
    def on_focus(self, instance, value):
        """Изменяет цвет границы при фокусе"""
        if value:
            self.border_color.rgba = (0.6, 0.6, 0.6, 1)
        else:
            self.border_color.rgba = (0.3, 0.3, 0.3, 1)
    
    def get_text(self):
        return self.text_input.text
    
    def clear_text(self):
        self.text_input.text = ''


class VideoBackground(FloatLayout):
    """Видео фон с циклическим воспроизведением"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        video_path = VIDEO_PATH
        if os.path.exists(video_path):
            try:
                self.video = Video(source=video_path, state='play', options={'eos': 'loop'}, size_hint=(1,1), pos_hint={'x':0,'y':0})
                with self.canvas.after:
                    Color(0,0,0,0.7)
                    self.overlay = Rectangle(pos=self.pos, size=self.size)
                self.add_widget(self.video)
                self.video.bind(state=self.on_video_state)
                self.bind(size=self._update_overlay, pos=self._update_overlay)
            except Exception as e:
                self.create_solid_background()
        else:
            self.create_solid_background()
    
    def create_solid_background(self):
        """Создает черный фон вместо видео"""
        with self.canvas.before:
            Color(0,0,0,1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def on_video_state(self, instance, value):
        """Перезапускает видео при завершении"""
        if value == 'stop':
            instance.state = 'play'
            instance.position = 0
    
    def _update_overlay(self, instance, value):
        """Обновляет позицию темного слоя"""
        if hasattr(self, 'overlay'):
            self.overlay.pos = instance.pos
            self.overlay.size = instance.size
    
    def _update_rect(self, instance, value):
        """Обновляет позицию черного фона"""
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size


class DeadVPNButton(FloatLayout):
    """Главная кнопка VPN с анимацией"""
    scale = NumericProperty(1.0)
    
    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.is_connected = False
        self.scale = 1.0
        with self.canvas.before:
            self.outer_color = Color(0.3,0.3,0.3,1)
            self.outer_ring = Ellipse(pos=(0,0), size=(0,0))
            self.inner_color = Color(0,0,0,0.8)
            self.inner_circle = Ellipse(pos=(0,0), size=(0,0))
        self.status_text = Label(text='OFF', font_size='24sp', color=(0.5,0.5,0.5,1), pos_hint={'center_x':0.5,'center_y':0.5}, bold=True)
        self.add_widget(self.status_text)
        self.bind(size=self.update_graphics, pos=self.update_graphics, scale=self.update_graphics)
    
    def update_graphics(self, *args):
        if self.size[0] == 0:
            return
        center_x, center_y = self.x + self.width/2, self.y + self.height/2
        radius = min(self.width, self.height)/2 * 0.9
        outer_size = radius * 2 * self.scale
        self.outer_ring.pos = (center_x - outer_size/2, center_y - outer_size/2)
        self.outer_ring.size = (outer_size, outer_size)
        inner_size = radius * 1.6 * self.scale
        self.inner_circle.pos = (center_x - inner_size/2, center_y - inner_size/2)
        self.inner_circle.size = (inner_size, inner_size)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.animate_press()
            if self.callback:
                self.callback(self)
            return True
        return super().on_touch_down(touch)
    
    def animate_press(self):
        anim = Animation(scale=0.95, duration=0.08)
        anim += Animation(scale=1.0, duration=0.15, t='out_bounce')
        anim.start(self)
        self.is_connected = not self.is_connected
        self.update_dead_state()
    
    def update_dead_state(self):
        if self.is_connected:
            self.outer_color.rgba = (0.8,0.8,0.8,1)
            self.status_text.text = 'ON'
            self.status_text.color = (0.9,0.9,0.9,1)
        else:
            self.outer_color.rgba = (0.3,0.3,0.3,1)
            self.status_text.text = 'OFF'
            self.status_text.color = (0.5,0.5,0.5,1)


class RegionButton(BoxLayout):
    """Кнопка региона"""
    def __init__(self, country_name, flag_url, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.country_name = country_name
        self.callback = callback
        self.selected = False
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.padding = [10,5]
        self.spacing = 15
        with self.canvas.before:
            self.bg_color = Color(0.1,0.1,0.1,0.9)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
            self.border_color = Color(0.3,0.3,0.3,1)
            self.border = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
        flag_container = FloatLayout(size_hint=(None,None), size=(40,60))
        self.flag_image = Image(source=flag_url if os.path.exists(flag_url) else '', size_hint=(None,None), size=(32,32), pos_hint={'center_x':0.5,'center_y':0.5}, allow_stretch=True, keep_ratio=False)
        flag_container.add_widget(self.flag_image)
        self.add_widget(flag_container)
        self.country_label = Label(text=country_name, font_size='16sp', color=(0.7,0.7,0.7,1), halign='left', valign='middle', size_hint_x=0.7, text_size=(200,None))
        self.country_label.bind(size=self._update_text_size)
        self.add_widget(self.country_label)
        self.selection_indicator = Label(text='', font_size='18sp', size_hint_x=0.1, color=(0.8,0.8,0.8,1))
        self.add_widget(self.selection_indicator)
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def _update_text_size(self, instance, value):
        instance.text_size = (instance.width, instance.height)
    
    def update_graphics(self, *args):
        self.bg.pos = (self.pos[0]+1, self.pos[1]+1)
        self.bg.size = (self.size[0]-2, self.size[1]-2)
        self.border.pos = self.pos
        self.border.size = self.size
    
    def set_selected(self, selected):
        self.selected = selected
        if selected:
            self.border_color.rgba = (0.5,0.5,0.5,1)
            self.country_label.color = (0.9,0.9,0.9,1)
            self.selection_indicator.text = ' '
        else:
            self.border_color.rgba = (0.3,0.3,0.3,1)
            self.country_label.color = (0.7,0.7,0.7,1)
            self.selection_indicator.text = ''
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback(self)
            return True
        return super().on_touch_down(touch)


class RegionSelectionPopup(Popup):
    """Попап выбора региона"""
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.selected_region = None
        self.title = 'SELECT REGION'
        self.size_hint = (0.9,0.8)
        self.auto_dismiss = False
        self.background_color = (0,0,0,0.9)
        self.title_color = (0.8,0.8,0.8,1)
        self.separator_color = (0.3,0.3,0.3,1)
        content = FloatLayout()
        scroll = ScrollView(size_hint=(0.9,0.7), pos_hint={'center_x':0.5,'center_y':0.55}, do_scroll_x=False)
        regions_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=[10,10])
        regions_layout.bind(minimum_height=regions_layout.setter('height'))
        
        # Получаем правильные пути к флагам
        data_dir = get_data_dir()
        countries = [
            ('USA', os.path.join(data_dir, 'flags', 's1.png')),
            ('UNITED KINGDOM', os.path.join(data_dir, 'flags', 's5.png')),
            ('GERMANY', os.path.join(data_dir, 'flags', 's6.png')),
            ('JAPAN', os.path.join(data_dir, 'flags', 's4.png')),
            ('CANADA', os.path.join(data_dir, 'flags', 's3.png')),
            ('FRANCE', os.path.join(data_dir, 'flags', 's2.png'))
        ]
        
        self.region_buttons = []
        for country, flag_path in countries:
            btn = RegionButton(country, flag_path, callback=self.on_region_select, size_hint_y=None, height=60)
            regions_layout.add_widget(btn)
            self.region_buttons.append(btn)
        self.set_current_region_selected()
        scroll.add_widget(regions_layout)
        content.add_widget(scroll)
        confirm_btn = DeadButton(text='CONFIRM SELECTION', callback=self.confirm_selection, size_hint=(0.8,None), height=50, pos_hint={'center_x':0.5,'y':0.05}, font_size='16sp')
        content.add_widget(confirm_btn)
        self.content = content
    
    def set_current_region_selected(self):
        for btn in self.region_buttons:
            if btn.country_name == self.main_app.current_region:
                btn.set_selected(True)
                self.selected_region = btn
                break
    
    def on_region_select(self, region_btn):
        for btn in self.region_buttons:
            btn.set_selected(False)
        region_btn.set_selected(True)
        self.selected_region = region_btn
    
    def confirm_selection(self, instance):
        if self.selected_region:
            self.main_app.current_region = self.selected_region.country_name
            self.main_app.dead_status.update_dead_status(self.main_app.dead_button.is_connected, self.main_app.current_region)
        self.dismiss()


class DeadButton(FloatLayout):
    """Универсальная кнопка с анимацией"""
    def __init__(self, text, callback=None, font_size='16sp', **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        with self.canvas.before:
            self.border_color = Color(0.2,0.2,0.2,1)
            self.border = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            self.bg_color = Color(0.05,0.05,0.05,0.9)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.text_label = Label(text=text, font_size=font_size, color=(0.7,0.7,0.7,1), pos_hint={'center_x':0.5,'center_y':0.5})
        self.add_widget(self.text_label)
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def update_graphics(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size
        self.bg.pos = (self.pos[0]+2, self.pos[1]+2)
        self.bg.size = (self.size[0]-4, self.size[1]-4)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(self.width*0.95, self.height*0.95), duration=0.08)
            anim += Animation(size=(self.width, self.height), duration=0.15, t='out_bounce')
            anim.start(self)
            anim_color = Animation(rgba=(0.1,0.1,0.1,1), duration=0.08) + Animation(rgba=(0.05,0.05,0.05,0.9), duration=0.15)
            anim_color.start(self.bg_color)
            if self.callback:
                Clock.schedule_once(lambda dt: self.callback(self), 0.2)
            return True
        return super().on_touch_down(touch)


class PlusButton(FloatLayout):
    """Кнопка плюс для добавления конфига"""
    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        with self.canvas.before:
            self.bg_color = Color(0.2, 0.2, 0.2, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        
        with self.canvas:
            self.line_color = Color(0.8, 0.8, 0.8, 1)
            self.line_h = Rectangle(pos=(0, 0), size=(0, 0))
            self.line_v = Rectangle(pos=(0, 0), size=(0, 0))
        
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def update_graphics(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        line_length = min(self.width, self.height) * 0.5
        line_width = 3
        
        self.line_h.pos = (center_x - line_length / 2, center_y - line_width / 2)
        self.line_h.size = (line_length, line_width)
        
        self.line_v.pos = (center_x - line_width / 2, center_y - line_length / 2)
        self.line_v.size = (line_width, line_length)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(self.width * 0.9, self.height * 0.9), duration=0.08)
            anim += Animation(size=(self.width, self.height), duration=0.15, t='out_bounce')
            anim.start(self)
            if self.callback:
                Clock.schedule_once(lambda dt: self.callback(self), 0.1)
            return True
        return super().on_touch_down(touch)


class DeadStatusPanel(FloatLayout):
    """Панель статуса подключения"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.border_color = Color(0.15,0.15,0.15,0.9)
            self.border = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
            self.bg_color = Color(0,0,0,0.8)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
        info_layout = BoxLayout(orientation='vertical', size_hint=(0.9,0.8), pos_hint={'center_x':0.5,'center_y':0.5}, spacing=8)
        self.status_label = Label(text='DISCONNECTED', font_size='14sp', color=(0.4,0.4,0.4,1), bold=True)
        self.ip_label = Label(text='IP: HIDDEN', font_size='12sp', color=(0.3,0.3,0.3,1))
        self.location_label = Label(text='LOCATION: USA', font_size='12sp', color=(0.3,0.3,0.3,1))
        info_layout.add_widget(self.status_label)
        info_layout.add_widget(self.ip_label)
        info_layout.add_widget(self.location_label)
        self.add_widget(info_layout)
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def update_graphics(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size
        self.bg.pos = (self.pos[0]+1, self.pos[1]+1)
        self.bg.size = (self.size[0]-2, self.size[1]-2)
    
    def update_dead_status(self, connected, region='USA'):
        if connected:
            self.status_label.text = 'CONNECTED'
            self.status_label.color = (0.8,0.8,0.8,1)
            self.ip_label.text = 'IP: 192.168.1.1'
            self.ip_label.color = (0.6,0.6,0.6,1)
            self.location_label.text = f'LOCATION: {region}'
            self.location_label.color = (0.6,0.6,0.6,1)
        else:
            self.status_label.text = 'DISCONNECTED'
            self.status_label.color = (0.4,0.4,0.4,1)
            self.ip_label.text = 'IP: HIDDEN'
            self.ip_label.color = (0.3,0.3,0.3,1)
            self.location_label.text = f'LOCATION: {region}'
            self.location_label.color = (0.3,0.3,0.3,1)


class ConfigInputScreen(FloatLayout):
    """Экран первого запуска для ввода конфига"""
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        
        title = Label(
            text='IKISKY',
            font_size='42sp',
            color=(0.9, 0.9, 0.9, 1),
            bold=True,
            size_hint=(1, None),
            height=80,
            pos_hint={'x': 0, 'top': 0.9}
        )
        self.add_widget(title)
        
        hint_label = Label(
            text='Введите конфигурацию VPN для подключения',
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(0.85, None),
            height=80,
            pos_hint={'center_x': 0.5, 'center_y': 0.57}
        )
        self.add_widget(hint_label)
        
        input_container = FloatLayout(
            size_hint=(0.85, None),
            height=50,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        self.config_input = DeadInput(
            hint_text='Введите свой конфиг',
            size_hint=(0.82, 1),
            pos_hint={'x': 0, 'center_y': 0.5}
        )
        input_container.add_widget(self.config_input)
        
        plus_btn = PlusButton(
            callback=self.on_add_config,
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'right': 1, 'center_y': 0.5}
        )
        input_container.add_widget(plus_btn)
        
        self.add_widget(input_container)
        
        self.error_label = Label(
            text='',
            font_size='13sp',
            color=(1, 0.3, 0.3, 1),
            size_hint=(0.85, None),
            height=30,
            pos_hint={'center_x': 0.5, 'center_y': 0.4}
        )
        self.add_widget(self.error_label)
        
        info_label = Label(
            text='',
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(0.85, None),
            height=40,
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        self.add_widget(info_label)
    
    def on_add_config(self, instance):
        config = self.config_input.get_text().strip()
        
        if not config:
            self.error_label.text = 'Пожалуйста, введите конфигурацию'
            return
        
        if len(config) < 10:
            self.error_label.text = 'Конфигурация слишком короткая'
            return
        
        if self.main_app.config_db.save_config(config):
            self.error_label.color = (0.3, 1, 0.3, 1)
            self.error_label.text = 'Конфигурация сохранена!'
            Clock.schedule_once(lambda dt: self.main_app.show_main_interface(), 1)
        else:
            self.error_label.color = (1, 0.3, 0.3, 1)
            self.error_label.text = 'Ошибка сохранения конфигурации'


class HamburgerMenu(DropDown):
    """Выпадающее меню гамбургера"""
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.auto_width = False
        self.width = 240
        self.max_height = 180
        self.background_color = (0.05,0.05,0.05,0.95)
        self.border = [10,10,10,10]
        self.create_menu_buttons()
    
    def create_menu_buttons(self):
        add_config_btn = DeadButton(
            text='Добавить конфигурацию',
            callback=self.add_config,
            size_hint_y=None,
            height=55,
            font_size='15sp'
        )
        self.add_widget(add_config_btn)
        
        support_btn = DeadButton(
            text='Support',
            callback=self.open_support,
            size_hint_y=None,
            height=55,
            font_size='15sp'
        )
        self.add_widget(support_btn)
    
    def add_config(self, instance):
        self.dismiss()
        self.main_app.open_add_config_popup()
    
    def open_support(self, instance):
        self.dismiss()
        self.main_app.open_support_popup()


class HamburgerIcon(Button):
    """Кнопка гамбургера"""
    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.callback = callback
        self.background_color = (0.2,0.2,0.2,1)
        self.size_hint = (None,None)
        self.size = (40,40)
        self.radius = [8,8,8,8]
        with self.canvas:
            self.line_color = Color(0.8,0.8,0.8,1)
            self.line1 = Rectangle(pos=(self.x+10, self.y+self.height-15), size=(self.width-20, 2))
            self.line2 = Rectangle(pos=(self.x+10, self.y+self.height/2-1), size=(self.width-20, 2))
            self.line3 = Rectangle(pos=(self.x+10, self.y+13), size=(self.width-20, 2))
        self.bind(pos=self.update_lines, size=self.update_lines)
    
    def update_lines(self, *args):
        self.line1.pos = (self.x+10, self.y+self.height-15)
        self.line1.size = (self.width-20, 2)
        self.line2.pos = (self.x+10, self.y+self.height/2-1)
        self.line2.size = (self.width-20, 2)
        self.line3.pos = (self.x+10, self.y+13)
        self.line3.size = (self.width-20, 2)
    
    def on_press(self):
        if self.callback:
            self.callback(self)
        anim = Animation(size=(self.width*0.95, self.height*0.95), duration=0.08)
        anim += Animation(size=(self.width, self.height), duration=0.15, t='out_bounce')
        anim.start(self)
        anim_color = Animation(background_color=(0.3,0.3,0.3,1), duration=0.08) + Animation(background_color=(0.2,0.2,0.2,1), duration=0.15)
        anim_color.start(self)
        self.animate_lines()
    
    def animate_lines(self):
        def animate_line(line, original_size):
            anim1 = Animation(size=(original_size[0], 1.5), duration=0.05)
            anim2 = Animation(size=original_size, duration=0.05)
            anim1.start(line)
            anim1.bind(on_complete=lambda *x: anim2.start(line))
        line1_size = self.line1.size
        line2_size = self.line2.size
        line3_size = self.line3.size
        animate_line(self.line1, line1_size)
        animate_line(self.line2, line2_size)
        animate_line(self.line3, line3_size)


class AddConfigPopup(Popup):
    """Попап для добавления новой конфигурации"""
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.title = 'ДОБАВИТЬ КОНФИГУРАЦИЮ'
        self.size_hint = (0.9, 0.6)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.95)
        self.title_color = (0.8, 0.8, 0.8, 1)
        self.separator_color = (0.3, 0.3, 0.3, 1)
        
        content = FloatLayout()
        
        input_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, None),
            height=180,
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            spacing=15,
            padding=[0, 20]
        )
        
        info_label = Label(
            text='Введите новую конфигурацию VPN:',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=30
        )
        input_layout.add_widget(info_label)
        
        self.config_input = DeadInput(
            hint_text='Введите конфигурацию...',
            multiline=True
        )
        self.config_input.height = 80
        input_layout.add_widget(self.config_input)
        
        self.error_label = Label(
            text='',
            font_size='12sp',
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=30
        )
        input_layout.add_widget(self.error_label)
        
        content.add_widget(input_layout)
        
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.8, None),
            height=50,
            pos_hint={'center_x': 0.5, 'y': 0.12},
            spacing=10
        )
        
        save_btn = DeadButton(
            text='СОХРАНИТЬ',
            callback=self.save_config,
            font_size='15sp'
        )
        
        cancel_btn = DeadButton(
            text='ОТМЕНА',
            callback=lambda x: self.dismiss(),
            font_size='15sp'
        )
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        self.content = content
    
    def save_config(self, instance):
        config = self.config_input.get_text().strip()
        
        if not config:
            self.error_label.text = 'Введите конфигурацию VPN для подключения'
            return
        
        if len(config) < 10:
            self.error_label.text = 'Конфигурация слишком короткая'
            return
        
        if self.main_app.config_db.save_config(config):
            self.error_label.color = (0.3, 1, 0.3, 1)
            self.error_label.text = 'Конфигурация обновлена!'
            Clock.schedule_once(lambda dt: self.dismiss(), 1)
        else:
            self.error_label.color = (1, 0.3, 0.3, 1)
            self.error_label.text = 'Ошибка сохранения'


class SupportPopup(Popup):
    """Попап поддержки"""
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.title = 'SUPPORT'
        self.size_hint = (0.9, 0.65)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.95)
        self.title_color = (0.8, 0.8, 0.8, 1)
        self.separator_color = (0.3, 0.3, 0.3, 1)
        
        content = FloatLayout()
        
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, None),
            height=280,
            pos_hint={'center_x': 0.5, 'center_y': 0.58},
            spacing=18,
            padding=[15, 20]
        )
        
        welcome_label = Label(
            text='Нужна помощь?',
            font_size='20sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
            height=40,
            bold=True
        )
        info_layout.add_widget(welcome_label)
        
        description_label = Label(
            text='Мы готовы помочь вам с любыми\nвопросами по использованию IKISKY VPN',
            font_size='13sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=50,
            halign='center'
        )
        info_layout.add_widget(description_label)
        
        contact_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            spacing=10
        )
        
        email_label = Label(
            text='Email: support@ikisky.com',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=30
        )
        
        telegram_label = Label(
            text='Telegram: @ikisky_support',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=30
        )
        
        hours_label = Label(
            text='Время работы: 24/7',
            font_size='13sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=30
        )
        
        contact_box.add_widget(email_label)
        contact_box.add_widget(telegram_label)
        contact_box.add_widget(hours_label)
        
        info_layout.add_widget(contact_box)
        
        content.add_widget(info_layout)
        
        close_btn = DeadButton(
            text='ЗАКРЫТЬ',
            callback=lambda x: self.dismiss(),
            size_hint=(0.7, None),
            height=50,
            pos_hint={'center_x': 0.5, 'y': 0.08},
            font_size='16sp'
        )
        
        content.add_widget(close_btn)
        self.content = content


class VPNApp(App):
    """Основное приложение VPN"""
    def build(self):
        self.current_region = 'USA'
        self.config_db = ConfigDatabase(CONFIG_FILE)
        self.region_popup = None
        self.hamburger_menu = None
        
        self.root = FloatLayout()
        self.video_bg = VideoBackground(size_hint=(1,1))
        self.root.add_widget(self.video_bg)
        
        if not self.config_db.has_config():
            self.show_config_input()
        else:
            self.show_main_interface()
        
        return self.root
    
    def show_config_input(self):
        """Показывает экран ввода конфига"""
        self.config_screen = ConfigInputScreen(self)
        self.root.add_widget(self.config_screen)
    
    def show_main_interface(self):
        """Показывает основной интерфейс"""
        if hasattr(self, 'config_screen'):
            self.root.remove_widget(self.config_screen)
        
        self.main_interface = FloatLayout(size_hint=(1,1))
        
        title = Label(
            text='IKISKY',
            font_size='42sp',
            color=(0.9, 0.9, 0.9, 1),
            bold=True,
            size_hint=(1, None),
            height=60,
            pos_hint={'x': 0, 'top': 0.95}
        )
        self.main_interface.add_widget(title)
        
        hamburger_btn = HamburgerIcon(
            callback=self.open_hamburger_menu,
            pos_hint={'right': 0.95, 'top': 0.95}
        )
        self.main_interface.add_widget(hamburger_btn)
        
        region_btn = DeadButton(
            text='SELECT REGION',
            callback=self.open_region_popup,
            size_hint=(0.8, None),
            height=45,
            pos_hint={'center_x': 0.5, 'top': 0.8},
            font_size='16sp'
        )
        self.main_interface.add_widget(region_btn)
        
        self.dead_button = DeadVPNButton(
            callback=self.toggle_dead_vpn,
            size_hint=(None, None),
            size=(220, 220),
            pos_hint={'center_x': 0.5, 'center_y': 0.45}
        )
        self.main_interface.add_widget(self.dead_button)
        
        self.dead_status = DeadStatusPanel(
            size_hint=(0.8, None),
            height=90,
            pos_hint={'center_x': 0.5, 'y': 0.15}
        )
        self.main_interface.add_widget(self.dead_status)
        
        footer = Label(
            text='CONNECTION STATUS',
            font_size='10sp',
            color=(0.4, 0.4, 0.4, 1),
            size_hint=(1, None),
            height=30,
            pos_hint={'x': 0, 'y': 0.02}
        )
        self.main_interface.add_widget(footer)
        
        self.root.add_widget(self.main_interface)
    
    def toggle_dead_vpn(self, instance):
        """Переключает состояние VPN"""
        self.dead_status.update_dead_status(self.dead_button.is_connected, self.current_region)
    
    def open_region_popup(self, instance):
        """Открывает попап выбора региона"""
        self.region_popup = RegionSelectionPopup(self)
        self.region_popup.open()
    
    def open_hamburger_menu(self, instance):
        """Открывает меню гамбургера"""
        if not self.hamburger_menu:
            self.hamburger_menu = HamburgerMenu(self)
        self.hamburger_menu.open(instance)
    
    def open_add_config_popup(self):
        """Открывает попап добавления конфигурации"""
        add_config_popup = AddConfigPopup(self)
        add_config_popup.open()
    
    def open_support_popup(self):
        """Открывает попап поддержки"""
        support_popup = SupportPopup(self)
        support_popup.open()


if __name__ == '__main__':
    VPNApp().run()