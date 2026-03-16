import os
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock, mainthread
from kivy.utils import platform
from kivy.core.window import Window

# Set clear black background for the app
Window.clearcolor = (0.05, 0.05, 0.05, 1)

if platform == 'android':
    from jnius import autoclass, cast
    from android import activity

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
    ImageReader = autoclass('android.media.ImageReader')
    PixelFormat = autoclass('android.graphics.PixelFormat')
    DisplayMetrics = autoclass('android.util.DisplayMetrics')
    DisplayManager = autoclass('android.hardware.display.DisplayManager')
    Activity = autoclass('android.app.Activity')
    
    Bitmap = autoclass('android.graphics.Bitmap')
    BitmapConfig = autoclass('android.graphics.Bitmap$Config')
    ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
    CompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')

    # Notification Classes
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
    String = autoclass('java.lang.String')

class OracleApp(App):
    def build(self):
        self.is_running = False
        
        # UI Setup: Dark, Minimalist INTJ Aesthetic
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=30)
        
        self.label = Label(
            text='[color=8A2BE2]S24 Oracle[/color]\n[color=00FF00]Awaiting Initialization...[/color]',
            halign='center',
            valign='middle',
            markup=True,
            font_size='18sp'
        )
        self.label.bind(size=self.label.setter('text_size'))
        
        self.btn = Button(
            text='[b]AWAKEN ORACLE[/b]', 
            size_hint=(1, 0.2),
            background_normal='',
            background_color=(0.1, 0.1, 0.1, 1),
            color=(0.54, 0.17, 0.89, 1), # Violet text
            markup=True,
            font_size='20sp'
        )
        self.btn.bind(on_press=self.toggle_oracle)
        
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.btn)
        
        if platform == 'android':
            activity.bind(on_activity_result=self.on_activity_result)
            self.setup_notifications()
            
        return self.layout

    def setup_notifications(self):
        if platform == 'android':
            context = PythonActivity.mActivity
            self.notification_manager = cast('android.app.NotificationManager', 
                                             context.getSystemService(Context.NOTIFICATION_SERVICE))
            
            # Create high-importance channel for Android 8.0+
            channel_id = String("oracle_channel")
            channel_name = String("S24 Oracle Predictions")
            importance = NotificationManager.IMPORTANCE_HIGH
            channel = NotificationChannel(channel_id, channel_name, importance)
            channel.setDescription(String("Displays RNG predictions over games."))
            
            self.notification_manager.createNotificationChannel(channel)

    def send_notification(self, title, content):
        if platform == 'android':
            context = PythonActivity.mActivity
            channel_id = String("oracle_channel")
            
            # Using Android's default notification icon since we don't have a custom drawable yet
            R_drawable = autoclass('android.R$drawable')
            
            builder = NotificationCompatBuilder(context, channel_id)
            builder.setSmallIcon(R_drawable.ic_dialog_info)
            builder.setContentTitle(String(title))
            builder.setContentText(String(content))
            builder.setPriority(1) # NotificationCompat.PRIORITY_HIGH
            builder.setCategory(String("msg")) # NotificationCompat.CATEGORY_MESSAGE
            
            notification = builder.build()
            self.notification_manager.notify(1, notification)

    def toggle_oracle(self, instance):
        if not self.is_running:
            if platform == 'android':
                self.update_label("[color=8A2BE2]Requesting MediaProjection...[/color]")
                context = PythonActivity.mActivity
                self.mpm = cast('android.media.projection.MediaProjectionManager', 
                                context.getSystemService(Context.MEDIA_PROJECTION_SERVICE))
                intent = self.mpm.createScreenCaptureIntent()
                PythonActivity.mActivity.startActivityForResult(intent, 1000)
            else:
                self.update_label("[color=FF0000]System is not running on Android.[/color]")
        else:
            self.is_running = False
            self.btn.text = "[b]AWAKEN ORACLE[/b]"
            self.btn.color = (0.54, 0.17, 0.89, 1) # Violet
            self.update_label("[color=8A2BE2]Oracle loop stopped.[/color]")
            if hasattr(self, 'virtual_display') and self.virtual_display:
                self.virtual_display.release()
            if hasattr(self, 'media_projection') and self.media_projection:
                self.media_projection.stop()

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == 1000:
            if platform == 'android':
                if resultCode == Activity.RESULT_OK:
                    self.update_label("[color=00FF00]Permission Granted![/color]\n[color=8A2BE2]Initializing The Brain...[/color]")
                    self.is_running = True
                    self.btn.text = "[b]SLEEP ORACLE[/b]"
                    self.btn.color = (0.1, 0.8, 0.1, 1) # Green
                    self.media_projection = self.mpm.getMediaProjection(resultCode, intent)
                    self.setup_virtual_display()
                    threading.Thread(target=self.oracle_loop, daemon=True).start()
                else:
                    self.update_label("[color=FF0000]Permission Denied by user.[/color]")

    def setup_virtual_display(self):
        context = PythonActivity.mActivity
        windowManager = context.getSystemService(Context.WINDOW_SERVICE)
        metrics = DisplayMetrics()
        windowManager.getDefaultDisplay().getMetrics(metrics)
        
        self.width = metrics.widthPixels
        self.height = metrics.heightPixels
        self.density = metrics.densityDpi

        self.image_reader = ImageReader.newInstance(self.width, self.height, PixelFormat.RGBA_8888, 2)
        
        self.virtual_display = self.media_projection.createVirtualDisplay(
            "OracleDisplay",
            self.width,
            self.height,
            self.density,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            self.image_reader.getSurface(),
            None,
            None
        )

    def image_to_bytes(self, image):
        planes = image.getPlanes()
        buffer = planes[0].getBuffer()
        pixelStride = planes[0].getPixelStride()
        rowStride = planes[0].getRowStride()
        rowPadding = rowStride - pixelStride * self.width
        
        bitmap = Bitmap.createBitmap(int(rowStride / pixelStride), self.height, BitmapConfig.ARGB_8888)
        bitmap.copyPixelsFromBuffer(buffer)
        
        if rowPadding > 0:
            bitmap = Bitmap.createBitmap(bitmap, 0, 0, self.width, self.height)
            
        stream = ByteArrayOutputStream()
        bitmap.compress(CompressFormat.JPEG, 80, stream)
        byte_array = stream.toByteArray()
        try:
            return bytes(byte_array)
        except TypeError:
            return byte_array.tostring()

    def oracle_loop(self):
        from google import genai
        from google.genai import types
        
        MODEL_ID = 'gemini-3-flash-preview'
        with open("config.txt", "r") as f:
            api_key = f.read().strip()
        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are the 'Psychic S24 Oracle'. Your goal is to identify RNG patterns in game screenshots. "
            "Analyze the visual layout, card positions, and historical context provided in the image. "
            "Do not describe the UI. Instead, provide a high-probability prediction for which slot (1, 2, or 3) "
            "is most likely to succeed. Explain your reasoning briefly using pattern-based terminology (e.g., 'offset logic', 'alternating sequence')."
        )
        
        while self.is_running:
            image = None
            try:
                image = self.image_reader.acquireLatestImage()
                if image:
                    self.update_label("[color=8A2BE2]Frame captured. The Brain is thinking...[/color]")
                    image_bytes = self.image_to_bytes(image)
                    image.close()
                    image = None
                    
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.2,
                        ),
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type='image/jpeg'
                            ),
                            "Predict the winning slot."
                        ]
                    )
                    prediction_text = response.text
                    print(f"Prediction received:\n{prediction_text}")
                    
                    # Try to parse for notification
                    title = "🔮 Psychic S24"
                    content = prediction_text
                    if "**Prediction:" in prediction_text:
                        try:
                            slot = prediction_text.split("**Prediction:")[1].split("**")[0].strip()
                            reasoning = prediction_text.split("**Reasoning:**")[1].strip()[:50]
                            content = f"Target: {slot} | {reasoning}..."
                        except:
                            pass
                            
                    self.send_notification(title, content)
                    self.update_label(f"[color=00FF00]Prediction:[/color]\n[color=8A2BE2]{prediction_text}[/color]")
                else:
                    pass 
            except Exception as e:
                self.update_label(f"[color=FF0000]Error in Brain:[/color] {str(e)}")
                if image:
                    try:
                        image.close()
                    except:
                        pass
            
            time.sleep(5)

    @mainthread
    def update_label(self, text):
        self.label.text = text

if __name__ == '__main__':
    OracleApp().run()