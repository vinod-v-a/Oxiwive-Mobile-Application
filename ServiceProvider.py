import io

import kivy
import re

from anvil import BlobMedia
from anvil.tables import app_tables
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivymd.uix.filemanager import MDFileManager
import sqlite3
from kivy.uix.image import AsyncImage
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.behaviors import CommonElevationBehavior
import anvil.server
# anvil.server.connect("server_42NNKDLPGUOK3E7FTS3LKXZR-2KOMXZYBNO22QB25")
import anvil.media
import os
import requests





Builder.load_file("service_register_form.kv")
Builder.load_file("service_provider.kv")
Builder.load_file("service_provider_main_page.kv")
Builder.load_file("ambulance_register_form.kv")
Builder.load_file("gym_register_form.kv")

#----------------------Rigistration form--------------------
class BaseRegistrationScreen(MDScreen):


    #------------------dropdowns---------------
    menu = ObjectProperty(None)
    menu2 = ObjectProperty(None)
    def open_dropdown(self, widget):
        if not self.menu:
            # Dropdown items
            cities = ["India"]
            items = [
                {
                    "text": city,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=city: self.select_city(x),
                } for city in cities
            ]
            # Create the dropdown menu with the caller property set
            self.menu = MDDropdownMenu(
                caller=widget,
                items=items,
                width_mult=3,
                max_height=300,
            )
        else:
            self.menu.dismiss()  # Dismiss if already open

        # Open the dropdown menu
        self.menu.open()

    def select_city(self, selected_city):
        # Callback function when a city is selected
        self.ids.Nation.text = selected_city  # Update the text field
        self.menu.dismiss()
    def open_dropdown2(self,widget):

        if not self.menu2:
            # Dropdown items
            cities = [
                        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
                        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
                        "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
                        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
                        "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
                        "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands",
                        "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
                        "Lakshadweep", "Delhi", "Puducherry"
                    ]
            items = [
                {
                    "text": city,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=city: self.select_state(x),
                } for city in cities
            ]
            # Create the dropdown menu
            self.menu2 = MDDropdownMenu(
                items=items,
                width_mult=6,
                max_height=400,
                pos_hint={'center_x':.1,'center_y':.9}
            )
        else:
            self.menu2.dismiss()  # Dismiss if already open

        # Set the caller and open the dropdown menu
        self.menu2.caller = self.ids.State
        self.menu2.open()

    def select_state(self, select_state):
        # Callback function when a city is selected
        #print(select_state)
        self.ids.State.text = select_state  # Update the text field
        self.menu2.dismiss()  # Dismiss the menu


    def on_save(self, instance, value, date_range):
        self.ids.extra_info2.text = str(value)

    # click Cancel
    def on_cancel(self, instance, value):
        #print("cancel")
        instance.dismiss()

    def show_date_picker(self,arg):
        date_dialog = MDDatePicker( size_hint=(None, None), size=(150, 150))
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
        self.ids.extra_info2.text=''
#------------------------------upload--docs--------------------------
    field_id=None
    def file_manager_open(self, field_id):
        self.field_id = getattr(self.ids, field_id)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,

        )
        self.file_manager.show('/')  # Initial directory when the file manager is opened

    path = None

    def select_path(self, path):
        if path.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            self.path = path
            setattr(self.field_id, 'text', path)
            self.file_manager.close()
        else:
            msg = "Please select a JPG, PNG, or PDF file."
            setattr(self.field_id, 'text', msg)
        self.file_manager.close()

    file_data1 = None
    file_data2 = None
    file_name1 = None
    file_name2 = None

    def upload_file(self, upload_id):
        try:
            file_path = getattr(self.field_id, 'text', '')
            if file_path:
                file_name = os.path.basename(file_path)
                file_data = self.read_file(file_path)
                setattr(self.field_id, 'text', file_name)

                if upload_id == "file_path":
                    self.file_data1 = file_data
                    self.file_name1 = file_name
                elif upload_id == "file_path2":
                    self.file_data2 = file_data
                    self.file_name2 = file_name
        except:
            msg = "Please select a file."
            setattr(self.field_id, 'text', msg)
    def read_file(self, file_path):
        with open(file_path, 'rb') as file:
            return file.read()

    def exit_manager(self, *args):
        self.file_manager.close()


#----------------------------------registration validation-------------

    def is_connected(self):
        try:
            # Attempt to make a simple HTTP request to check connectivity
            response = requests.get('https://www.google.com', timeout=5)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return True
        except requests.RequestException:
            return False

    def show_validation_dialog(self, message):
        # Display a dialog for invalid login or sign up
        dialog = MDDialog(
            text=message,
            elevation=0,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()
    def hospital_register_form(self, register_id):

        service_provider_name = self.ids.service_provider_name.text
        service_provider_email = self.ids.service_provider_email.text
        service_provider_password = self.ids.service_provider_password.text
        service_provider_phoneno = self.ids.service_provider_phoneno.text
        service_provider_address = self.ids.service_provider_address.text
        Nation=self.ids.Nation.text
        State=self.ids.State.text
        service_provider_pincode=self.ids.service_provider_pincode.text
        extra_info=self.ids.extra_info.text
        extra_info2=self.ids.extra_info2.text

        # Validation logic
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        is_valid_password, password_error_message = self.validate_password(service_provider_password)

        if not service_provider_name:
            self.ids.service_provider_name.error = True
            self.ids.service_provider_name.helper_text = "This field is required."
            self.ids.service_provider_name.required = True
        elif not service_provider_email or not re.match(email_regex, service_provider_email):
            self.ids.service_provider_email.error = True
            self.ids.service_provider_email.helper_text = "Invalid email format."
            self.ids.service_provider_email.required = True
        elif not is_valid_password:
            self.ids.service_provider_password.error = True
            self.ids.service_provider_password.helper_text =  password_error_message
            self.ids.service_provider_password.required = True
        elif not service_provider_phoneno or len(service_provider_phoneno) != 10:
            self.ids.service_provider_phoneno.error = True
            self.ids.service_provider_phoneno.helper_text = "Invalid phone number (10 digits required)."
            self.ids.service_provider_phoneno.required = True
        elif not service_provider_address:
            self.ids.service_provider_address.error = True
            self.ids.service_provider_address.helper_text = "This field is required."
            self.ids.service_provider_address.required = True
        elif not Nation:
            self.ids.Nation.error = True
            self.ids.Nation.helper_text = "Please select a nation."
            # self.ids.dropdown_nation.required = True
        elif not State:
            self.ids.State.error = True
            self.ids.State.helper_text = "Please select a state."
            # self.ids.dropdown_state.required = True
        elif not service_provider_pincode or len(service_provider_pincode) != 6:
            self.ids.service_provider_pincode.error = True
            self.ids.service_provider_pincode.helper_text = "Invalid pincode (6 digits required)."
            self.ids.service_provider_pincode.required = True
        elif not extra_info:
            self.ids.extra_info.error = True
            self.ids.extra_info.helper_text = "This field is required."
            self.ids.extra_info.required = True
        elif not extra_info2:
            self.ids.extra_info2.error = True
            self.ids.extra_info2.helper_text = "This field is required."
            # self.ids.est_year.required = True

        else:
            app = MDApp.get_running_app()
            if app.root.current=="service_register_form":
                print("------------------hospital_manager--------------")
                try:
                    media1 = BlobMedia(content_type="application/octet-stream", name=self.file_name1,
                                       content=self.file_data1)
                    media2 = BlobMedia(content_type="application/octet-stream", name=self.file_name2,
                                       content=self.file_data2)
                    if self.is_connected():
                        anvil.server.connect("server_42NNKDLPGUOK3E7FTS3LKXZR-2KOMXZYBNO22QB25")
                        rows = app_tables.hospital_register_form.search()
                        # Get the number of rows
                        num = len(rows) + 1
                        id = f"SP-{num}"
                        app_tables.hospital_register_form.add_row(
                            service_provider_id=id,
                            service_provider_name=service_provider_name,
                            service_provider_email=service_provider_email,
                            service_provider_password=service_provider_password,
                            service_provider_phoneno=float(service_provider_phoneno),
                            service_provider_address=service_provider_address,
                            Nation=Nation,
                            State=State,
                            service_provider_pincode=int(service_provider_pincode),
                            hospital_name=extra_info,
                            establisted_year=extra_info2,
                            Medical_Practitioner_License=media1,
                            Building_Permit_and_License=media2
                        )
                        app = MDApp.get_running_app()
                        app.root.transition.direction = "left"
                        app.root.current = "login"
                    else:
                        self.show_validation_dialog("No internet connection")
                except Exception as e:
                    print(e)
                    self.show_validation_dialog("Select file")

            elif app.root.current=="ambulance_register_form":
                print("----------------ambulance_manager--------------------")
                try:
                    media1 = BlobMedia(content_type="application/octet-stream", name=self.file_name1,
                                       content=self.file_data1)
                    media2 = BlobMedia(content_type="application/octet-stream", name=self.file_name2,
                                       content=self.file_data2)
                    if self.is_connected():
                        anvil.server.connect("server_42NNKDLPGUOK3E7FTS3LKXZR-2KOMXZYBNO22QB25")
                        rows = app_tables.ambulance_register_form.search()
                        # Get the number of rows
                        num = len(rows) + 1
                        id = f"SP-{num}"
                        app_tables.ambulance_register_form.add_row(
                            service_provider_id=id,
                            service_provider_name=service_provider_name,
                            service_provider_email=service_provider_email,
                            service_provider_password=service_provider_password,
                            service_provider_phoneno=float(service_provider_phoneno),
                            service_provider_address=service_provider_address,
                            Nation=Nation,
                            State=State,
                            service_provider_pincode=int(service_provider_pincode),
                            Vehicle_No=extra_info,
                            registered_year=extra_info2,
                            Vehicle_RC=media1,
                            Driver_DL=media2
                        )
                        app = MDApp.get_running_app()
                        app.root.transition.direction = "left"
                        app.root.current = "login"
                    else:
                        self.show_validation_dialog("No internet connection")
                except Exception as e:
                    print(e)
                    self.show_validation_dialog("Select file")

            elif app.root.current=="gym_register_form":
                print("---------------------gym_manager---------------------------")
                try:
                    media1 = BlobMedia(content_type="application/octet-stream", name=self.file_name1,
                                       content=self.file_data1)
                    media2 = BlobMedia(content_type="application/octet-stream", name=self.file_name2,
                                       content=self.file_data2)
                    if self.is_connected():
                        anvil.server.connect("server_42NNKDLPGUOK3E7FTS3LKXZR-2KOMXZYBNO22QB25")
                        rows = app_tables.gym_register_form.search()
                        # Get the number of rows
                        num = len(rows) + 1
                        id = f"SP-{num}"
                        app_tables.gym_register_form.add_row(
                            service_provider_id=id,
                            service_provider_name=service_provider_name,
                            service_provider_email=service_provider_email,
                            service_provider_password=service_provider_password,
                            service_provider_phoneno=float(service_provider_phoneno),
                            service_provider_address=service_provider_address,
                            Nation=Nation,
                            State=State,
                            service_provider_pincode=int(service_provider_pincode),
                            Gym_Name=extra_info,
                            establisted_year=extra_info2,
                            Gym_Registration=media1,
                            SSI_Registration=media2
                        )
                        app = MDApp.get_running_app()
                        app.root.transition.direction = "left"
                        app.root.current = "login"
                    else:
                        self.show_validation_dialog("No internet connection")
                except Exception as e:
                    print(e)
                    self.show_validation_dialog("Select file")
            self.ids.service_provider_name.text = ""
            self.ids.service_provider_email.text = ""
            self.ids.service_provider_password.text =""
            self.ids.service_provider_phoneno.text = ""
            self.ids.service_provider_address.text = ""
            self.ids.Nation.text = ""
            self.ids.State.text = ""
            self.ids.service_provider_pincode.text = ""
            self.ids.extra_info.text = ""
            self.ids.extra_info2.text = ""

    # password validation
    def validate_password(self, password):
        # Check if the password is not empty
        if not password:
            return False, "Password cannot be empty"

        # Check if the password has at least 8 characters
        if len(password) < 6:
            return False, "Password must have at least 6 characters"

        # Check if the password contains both uppercase and lowercase letters
        if not any(c.isupper() for c in password) or not any(c.islower() for c in password):
            return False, "Password must contain uppercase, lowercase"

        # Check if the password contains at least one digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        # Check if the password contains at least one special character
        special_characters = r"[!@#$%^&*(),.?\":{}|<>]"
        if not re.search(special_characters, password):
            return False, "Password must contain a special character"

        # All checks passed; the password is valid
        return True, "Password is valid"


class ServiceRegister(BaseRegistrationScreen):
    # Additional functionalities specific to ServiceRegister
    pass

class ServiceRegisterGym(BaseRegistrationScreen):
    # Additional functionalities specific to ServiceRegisterGym
    pass

class ServiceRegisterAmbulance(BaseRegistrationScreen):
    # Additional functionalities specific to ServiceRegisterAmbulance
    pass

#------------------------ServiceProvider--------------------

class ServiceProvider(MDScreen):

    def animate_button(self, button_id):
        original_button_size = (dp(290), dp(150))
        original_image_size = (dp(290), dp(150))

        # Create animation for the button size
        anim_button = Animation(size=(dp(280), dp(140)),  duration=0.2, transition="linear")
        anim_button += Animation(size=original_button_size,duration=0.2)

        # Create animation for the image size
        anim_image = Animation( size=(dp(280), dp(140)),duration=0.2, transition="linear")
        anim_image += Animation(size=original_image_size, duration=0.2)

        anim_button.start(self.ids[button_id])
        anim_image.start(self.ids[button_id].children[0])

        self.ids[button_id].elevation_normal = 0

        Clock.schedule_once(lambda dt: self.transition_to_service_register_form(button_id), 0.5)

    def transition_to_service_register_form(self, button_id):
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"

        if button_id == 'hospital_button':
            app.root.current = "service_register_form"
        elif button_id == 'ambulance_button':
            app.root.current = "ambulance_register_form"
        elif button_id == 'gym_button':
            app.root.current = "gym_register_form"
        # Add more conditions as needed for other buttons

#-------------------service provider main-----------------------
class ServiceProviderMain(MDScreen):
    menu = ObjectProperty(None)
    def service_button(self,button):
        if not self.menu:
            cities = ["Settings", "Notification"]
            items = [
                {
                    "text": city,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=city: self.select_city(x),
                } for city in cities
            ]

            # Use the first button from right_action_items as the caller



            self.menu = MDDropdownMenu(
                caller=button,
                items=items,
                width_mult=3,
                elevation=2,

                max_height = dp(100),

            )
        else:
            self.menu.dismiss()

        self.menu.open()

    def select_city(self, option):
        # Callback function when a city is selected
        if option == 'Settings':
            self.settings()
        elif option == 'Notification':
            self.notification_button_action()

        self.menu.dismiss()

    def settings(self):
        print("Settings")

    def notification_button_action(self):
        print("Notification")


    def sign_out_button_action(self):
        app = MDApp.get_running_app()
        app.root.transition.direction = "left"
        app.root.current = "login"
class ServiceProfile(MDScreen):
    pass

class ServiceNotification(MDScreen):
    pass



class ServiceSlotAdding(MDScreen):
    def __init__(self, **kwargs):
        super(ServiceSlotAdding, self).__init__(**kwargs)
        self.data_tables = MDDataTable(
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=True,
            check=True,
            column_data=[
                ("No.", dp(30)),
                ("Slot No", dp(40)),
                ("Applied Date", dp(40)),
                ("Status", dp(40)),
            ],
            row_data=[("1", "A1", "01-01-2024", ([1, 0, 0, 1],'pedding'))],
        )

        # Creating control buttons.
        button_box = MDBoxLayout(
            pos_hint={"center_x": 0.5},
            adaptive_size=True,
            padding="24dp",
            spacing="24dp",
        )

        for button_text in ["Add Slot",  "Delete Checked Slots"]:
            button_box.add_widget(
                MDRaisedButton(
                    text=button_text, on_release=self.on_button_press
                )
            )

        layout = MDFloatLayout()  # root layout
        layout.add_widget(self.data_tables)
        layout.add_widget(button_box)
        self.add_widget(layout)

    def on_button_press(self, instance_button):
        try:
            {
                "Add Slot": self.add_row,
                "Delete Checked Slots": self.delete_checked_rows,
            }[instance_button.text]()
        except KeyError:
            pass

    def add_row(self):
        last_num_row = int(self.data_tables.row_data[-1][0])
        new_row_data = (
            str(last_num_row + 1),
            "C1",
            "03-03-2024",
            ([1, 1, 0, 0], 'in progress')
        )
        self.data_tables.row_data.append(list(new_row_data))

    def delete_checked_rows(self):
        def deselect_rows(*args):
            self.data_tables.table_data.select_all("normal")

        checked_rows = self.data_tables.get_row_checks()
        for checked_row in checked_rows:
            if checked_row in self.data_tables.row_data:
                self.data_tables.row_data.remove(checked_row)

        Clock.schedule_once(deselect_rows)

class ServiceSupport(MDScreen):
    pass