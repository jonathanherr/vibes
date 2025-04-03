# main.py (Kivy/Python for Android)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty
from kivy.core.window import Window
import json
import webbrowser

class QuoteApp(App):
    quote_text = StringProperty("")
    book_title = StringProperty("")
    author = StringProperty("")
    image_source = StringProperty("")
    info_link = StringProperty("")

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10)

        self.quote_label = Label(text=self.quote_text, text_size=(Window.width * 0.9, None), halign='center', valign='middle')
        layout.add_widget(self.quote_label)

        self.image = Image(source=self.image_source, size_hint=(None, None), size=(200, 300))
        self.image.bind(on_touch_down=self.on_image_click)
        layout.add_widget(self.image)

        self.title_label = Label(text=self.book_title, bold=True)
        layout.add_widget(self.title_label)

        self.author_label = Label(text=self.author)
        layout.add_widget(self.author_label)

        self.fetch_quote()

        return layout

    def fetch_quote(self):
        url = "YOUR_API_ENDPOINT" # Replace with your API endpoint
        def on_success(req, result):
            data = json.loads(result)
            self.quote_text = data['quote']
            self.book_title = data['title']
            self.author = data['author']
            self.image_source = data['cover_image_url']
            self.info_link = data['info_link']
            self.quote_label.text = self.quote_text
            self.title_label.text = self.book_title
            self.author_label.text = self.author
            self.image.source = self.image_source

        def on_error(req, error):
            print("Error:", error)
            self.quote_text = "Failed to load quote."
            self.quote_label.text = self.quote_text

        def on_failure(req, failure):
            print("Failure:", failure)
            self.quote_text = "Network error."
            self.quote_label.text = self.quote_text

        UrlRequest(url, on_success, on_error, on_failure)

    def on_image_click(self, instance, touch):
        if instance.collide_point(*touch.pos) and self.info_link:
            webbrowser.open(self.info_link)

if __name__ == '__main__':
    QuoteApp().run()