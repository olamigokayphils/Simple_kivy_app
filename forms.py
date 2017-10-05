import random
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.weakproxy import WeakProxy
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, DictProperty
from kivy.properties import NumericProperty, ListProperty
from kivy.properties import ObjectProperty

#
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput




def get_parent(name=None, parent=None):
    if not name:
        return
    if name in str(parent):
        return parent
    else:
        return get_parent(name, parent.parent)

class MsgButton(Button):
    def __init__(self, **kwargs):
        """Parent Variable is available after __init__is completed, therefore we schedule a clock event,
            postprone working with  a parent until a next frame.
        """
        self.app = App.get_running_app()
        super(MsgButton, self).__init__(**kwargs)
        Clock.schedule_once(self.post_init)


    def post_init__(self, *args):
        """Get an instance of Form the widget is via tranversing the parent-children tree
            because the order of childern added to a custom layout is randomized.

        Setup an on release binding. It's important to notice passing an object of Form to partial, not
        just a string, because partial freezes everything in place.
        making this::

            partail(function, string)

        would leave the string unchanged in partial although it might change somewhere else durring the app cycle.

        """

        self.form = get_parent("Form", self.parent)
        part = partial(
            self.send_message,
            self.form, "ping from %s" % self
        )
        self.bind(on_release=part)

    def send_message(self, form, msg, *args):
        """if a target Form is available, change its bottom"""
        if form.msg_target:
            form.msg_target.ids.bottom.text = msg


class MsgSpinner(Spinner):
    def __init__(self, **kwargs):
        """Fetch created forms if available in dictionary.. create if otherwise"""

        wp = WeakProxy
        self.app = App.get_running_app()
        super(MsgSpinner, self).__init__(**kwargs)
        self.weak_values = self.app.area.weak_values

        for child in self.app.area.children:
            if "Form" in str(child):
                self.weak_values[str(child.title)] = wp(child)

        self.values = self.weak_values.keys()
        Clock.schedule_once(self.post_init)

    def on_text(self, *args):
        """update a message if selected  value of spinner changes"""
        self.form.msg_target = self.weak_values[self.text]

class FormItem(Button):
    """A taskbar-like item storing a reference to Form object. On click/tap restores the Form.
    """
    def __init__(self, area=None, formobj=None, **kwargs):
        super(FormItem, self).__init__(**kwargs)
        self.area = area
        self.formobj = formobj
        self.bind(on_release=self.restore)

    def restore(self, *args):
        """Restore a Form by adding it as  a  widget to Area as FormItem already hs
        the instance of Form stored in 'formobj' the instance is added unchanged.
        """

        self.area.add_widget(self.formobj)
        self.parent.remove_widget(self)

class Form(Scatter):
    """A dragable, scaleable window-like widget.
    """

    msg_target = ObjectProperty()
    old_pos = ListProperty([0, 0])
    old_size = ListProperty([0, 0])
    title = StringProperty("My Form")
    default_bottom = StringProperty("Bottom")


    def __init__(self, title="MyForm", content=None, bottom="", area=None, **kwargs):
        if not area or not content:
            raise Exception(
                "A form has to have both area it"
                "belongs to and widget content!")
        self.area = area
        self.title = title
        super(Form, self).__init__(**kwargs)
        self.ids.container.add_widgets(content)

    def minimize(self):
        """For minimizing we need to hide a  widget which is handled bwith remove_widget
        however such an action discards an instance of our Form. therefore we'll need to
        save it somewhere first.

        FormItem takes a direct reference of our form and as there is still a reference,
        the instance will be collected by garbage collector.
        """

        self.area.ids.formbar.add_widget(formitem)
        self.area.remove_widget(self)


    def maximise(self):
        if size != self.area.size:
            self.old_size = self.size
            self.old_pos = self.pos
            self.size = self.area.size
            self.pos = [0, self.area.formbar.height]
        else:
            self.size = self.old_size
            self.pos = self.old_pos

    def close(self):
        self.area.total_children -= 1
        self.area.remove_widget(self)

    def flush_ping(self, *args):
        """flush any other text than the default one in the bottom part of the Form"""

        if self.ids.bottom.text != self.default_bottom:
            self.ids.bottom.text = self.default_bottom


class Area(FloatLayout):
    """A widget for placing forms.. mustn't need to be a Floatlayout but must not restrict
        position of its children or depend on it any way"""
    total_children = NumericProperty(0)
    formbar_height = NumericProperty(0.05)
    available = ListProperty(
        [CheckBox, MsgButton, MsgSpinner, Switch, TextInput]
    )
    weak_value = DictProperty()

    def __init__(self, **kwargs):
        super(Area, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.app.area = self

    def create_form(self, *args):
        """create a form with the title "My Form N", where N is a count of the Forms
    in the Area and populates the Form content with a layout with randomized children.
    """
        self.total += 1
        title = "My Form %s" % self.total_children
        bottom = str(random.random())
        form = Form(title=title, content=self.pick_child(),
                    bottom=bottom, area=self)
        self.add_widget(form)

    def pick_child(self):
        avail = self.available
        children = random.sample(avail, len(avail))
        box = BoxLayout()

        left = children[0]()
        right = BoxLayout(orientation = "vertical")

        up = children[1]()
        mid = children[2]()
        down = BoxLayout()

        down_left = children[3]()
        down_right = children[4]()

        down.add_widget(down_left)
        down.add_widget(down_right)

        right.add_widget(up)
        right.add_widget(mid)
        right.add_widget(down)

        box.add_widget(left)
        box.add_widget(right)
        return box

class MultiForm(App):
    def build(self):
        return Area()

if "__name__" == "__main__":
    MultiForm().run()
