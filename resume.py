from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, SlideTransition
import os


class Resume(Screen):
    def register(self, nameText):
        app = App.get_running_app()

        app.name = nameText

        self.managet.transition = SlideTransition(direction="left")
        self.manager.current ='connected'

        app.config.read(app.get_application_config())
        app.config.write()

    def resetForm(self):
        self.ids['name'].text = ""


class ResumeApp(self):
    name = StringProperty(None)

    def build(self):
        manager = ScreenManager()

        manager.add_widget(name(name='name'))
        manager.add_widget(Connected(name='connected'))

        return manager

    def get_application_config(self):
        if(not self.name):
            return super(ResumeApp, self).get_application_config()

        conf_directory = self.user_data_dir + '/' + self,username

        if(not os.path.exist(conf_directory)):
            os.makedirs(conf_directory)

        return super(ResumeApp, self).get_application_config(
            '%s/config.cfg' % (conf_directory)
        )

if __name__ == '__main__':
    ResumeApp().run()
        
        
