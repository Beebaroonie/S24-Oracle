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
    from jnius import autoclass, cast, PythonJavaClass, java_method
    from android import activity
    from android.runnable import run_on_ui_thread

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    try:
        ServiceOracleservice = autoclass('org.psychic.s24oracle.ServiceOracleservice')
    except:
        pass
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

    # Overlay & Window Management Classes
    WindowManager = autoclass('android.view.WindowManager')
    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
    Gravity = autoclass('android.view.Gravity')
    Color = autoclass('android.graphics.Color')
    View = autoclass('android.view.View')
    Button_Android = autoclass('android.widget.Button')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
    MotionEvent = autoclass('android.view.MotionEvent')

    try:
        import cv2
        import numpy as np
    except ImportError:
        pass
        
    # UI Widgets for Viewport
    LinearLayout = autoclass('android.widget.LinearLayout')
    ScrollView = autoclass('android.widget.ScrollView')
    TextView = autoclass('android.widget.TextView')

class OracleApp(App):
    def build(self):
        self.is_running = False
        self.bubble_active = False
        
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
            self.check_overlay_permission()
            
        return self.layout

    def check_overlay_permission(self):
        if platform == 'android':
            context = PythonActivity.mActivity
            if not Settings.canDrawOverlays(context):
                self.update_label("[color=FF0000]OVERLAY PERMISSION REQUIRED[/color]\n[color=8A2BE2]Redirecting to settings...[/color]")
                intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
                intent.setData(Uri.parse(String("package:" + str(context.getPackageName()))))
                context.startActivity(intent)

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

    @run_on_ui_thread
    def spawn_bubble(self):
        if platform == 'android':
            context = PythonActivity.mActivity
            self.window_manager = cast('android.view.WindowManager', 
                                     context.getSystemService(Context.WINDOW_SERVICE))
            
            # Use TYPE_APPLICATION_OVERLAY for Android 8.0+
            # TYPE_APPLICATION_OVERLAY = 2038
            overlay_type = 2038
            
            self.bubble_params = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT,
                overlay_type,
                LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH,
                PixelFormat.TRANSLUCENT
            )
            
            self.bubble_params.gravity = Gravity.TOP | Gravity.LEFT
            self.bubble_params.x = 0
            self.bubble_params.y = 100
            
            self.bubble_btn = Button_Android(context)
            self.bubble_btn.setText(String("🔮"))
            self.bubble_btn.setBackgroundColor(Color.TRANSPARENT)
            self.bubble_btn.setTextColor(Color.MAGENTA)
            self.bubble_btn.setTextSize(30.0)
            
            # Implement OnTouchListener for dragging
            class BubbleTouchListener(PythonJavaClass):
                __javainterfaces__ = ['android/view/View$OnTouchListener']
                __javacontext__ = 'app'
                
                def __init__(self, app_instance):
                    super(BubbleTouchListener, self).__init__()
                    self.app = app_instance
                    self.initialX = 0
                    self.initialY = 0
                    self.initialTouchX = 0.0
                    self.initialTouchY = 0.0
                    self.isClick = False
                    
                @java_method('(Landroid/view/View;Landroid/view/MotionEvent;)Z')
                def onTouch(self, view, event):
                    action = event.getAction()
                    
                    if action == MotionEvent.ACTION_DOWN:
                        self.initialX = self.app.bubble_params.x
                        self.initialY = self.app.bubble_params.y
                        self.initialTouchX = event.getRawX()
                        self.initialTouchY = event.getRawY()
                        self.isClick = True
                        return True
                        
                    elif action == MotionEvent.ACTION_UP:
                        if self.isClick:
                            self.app.toggle_viewport()
                        return True
                        
                    elif action == MotionEvent.ACTION_MOVE:
                        dx = event.getRawX() - self.initialTouchX
                        dy = event.getRawY() - self.initialTouchY
                        if abs(dx) > 10 or abs(dy) > 10:
                            self.isClick = False
                            
                        self.app.bubble_params.x = int(self.initialX + dx)
                        self.app.bubble_params.y = int(self.initialY + dy)
                        self.app.window_manager.updateViewLayout(self.app.bubble_btn, self.app.bubble_params)
                        return True
                        
                    return False

            self.touch_listener = BubbleTouchListener(self)
            self.bubble_btn.setOnTouchListener(self.touch_listener)
            
            self.window_manager.addView(self.bubble_btn, self.bubble_params)
            self.bubble_active = True

    @run_on_ui_thread
    def remove_bubble(self):
        if platform == 'android' and hasattr(self, 'bubble_btn') and self.bubble_active:
            if hasattr(self, 'viewport_active') and self.viewport_active:
                self.hide_viewport()
            self.window_manager.removeView(self.bubble_btn)
            self.bubble_active = False

    def toggle_viewport(self):
        if not hasattr(self, 'viewport_active') or not self.viewport_active:
            self.show_viewport()
        else:
            self.hide_viewport()

    @run_on_ui_thread
    def show_viewport(self):
        if platform == 'android':
            context = PythonActivity.mActivity
            
            # Hide the bubble button
            self.bubble_btn.setVisibility(View.GONE)
            
            # Create Viewport Layout (20% vertical)
            self.viewport_layout = LinearLayout(context)
            self.viewport_layout.setOrientation(LinearLayout.VERTICAL)
            self.viewport_layout.setBackgroundColor(Color.parseColor("#CC000000")) # Semi-transparent black
            
            # Header
            header = TextView(context)
            header.setText(String("🔮 Oracle History (Tap to collapse)"))
            header.setTextColor(Color.MAGENTA)
            header.setTextSize(16.0)
            header.setPadding(20, 20, 20, 20)
            
            # Click header to collapse
            class HeaderTouchListener(PythonJavaClass):
                __javainterfaces__ = ['android/view/View$OnTouchListener']
                __javacontext__ = 'app'
                def __init__(self, app_instance):
                    super(HeaderTouchListener, self).__init__()
                    self.app = app_instance
                @java_method('(Landroid/view/View;Landroid/view/MotionEvent;)Z')
                def onTouch(self, view, event):
                    if event.getAction() == MotionEvent.ACTION_UP:
                        self.app.hide_viewport()
                    return True
            
            self.header_listener = HeaderTouchListener(self)
            header.setOnTouchListener(self.header_listener)
            
            self.viewport_layout.addView(header)
            
            # Scrollable History List
            scroll_view = ScrollView(context)
            self.history_layout = LinearLayout(context)
            self.history_layout.setOrientation(LinearLayout.VERTICAL)
            self.history_layout.setPadding(20, 0, 20, 20)
            
            # Placeholder for history items
            history_text = TextView(context)
            history_text.setText(String("Waiting for predictions..."))
            history_text.setTextColor(Color.WHITE)
            self.history_layout.addView(history_text)
            
            scroll_view.addView(self.history_layout)
            self.viewport_layout.addView(scroll_view)
            
            # Viewport Layout Params (20% width, full height)
            metrics = DisplayMetrics()
            self.window_manager.getDefaultDisplay().getMetrics(metrics)
            width = int(metrics.widthPixels * 0.20)
            height = metrics.heightPixels
            
            overlay_type = 2038
            self.viewport_params = LayoutParams(
                width,
                height,
                overlay_type,
                LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT
            )
            self.viewport_params.gravity = Gravity.TOP | Gravity.LEFT
            self.viewport_params.x = 0
            self.viewport_params.y = 0
            
            self.window_manager.addView(self.viewport_layout, self.viewport_params)
            self.viewport_active = True

    @run_on_ui_thread
    def hide_viewport(self):
        if platform == 'android' and hasattr(self, 'viewport_layout'):
            self.window_manager.removeView(self.viewport_layout)
            self.bubble_btn.setVisibility(View.VISIBLE)
            self.viewport_active = False

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
            self.remove_bubble()
            if hasattr(self, 'virtual_display') and self.virtual_display:
                self.virtual_display.release()
            if hasattr(self, 'media_projection') and self.media_projection:
                self.media_projection.stop()

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == 1000:
            if platform == 'android':
                if resultCode == Activity.RESULT_OK:
                    self.update_label("[color=00FF00]Permission Granted![/color]\n[color=8A2BE2]Initializing The Brain...[/color]")
                    try:
                        ServiceOracleservice.start(PythonActivity.mActivity, '')
                        time.sleep(0.5)
                    except Exception as e:
                        print('Service start error:', e)
                    self.is_running = True
                    self.btn.text = "[b]SLEEP ORACLE[/b]"
                    self.btn.color = (0.1, 0.8, 0.1, 1) # Green
                    self.spawn_bubble()
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
        import base64
        import json
        import urllib.request
        import urllib.error
        try:
            import cv2
            import numpy as np
            has_cv2 = True
        except ImportError:
            has_cv2 = False
        
        system_instruction = "You are the 'Psychic S24 Oracle'. You are an OCR and pattern recognition expert. You will receive an image consisting of 3 cropped slots (A, B, C) concatenated horizontally. Your task: Extract the integer values from each slot. Compare them. Output ONLY the slot letter (A, B, or C) that has the maximum value. If there is a tie, output all letters with the max value separated by commas. Explain your reasoning in exactly one short sentence."
        
        previous_state_hash = None
        
        while self.is_running:
            image = None
            try:
                image = self.image_reader.acquireLatestImage()
                if image:
                    image_bytes = self.image_to_bytes(image)
                    image.close()
                    image = None
                    
                    b64_image = ""
                    combined_np = None
                    
                    if has_cv2:
                        # Decode JPEG to Numpy Array
                        img_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
                        h, w, _ = img_np.shape
                        
                        # Define Static ROIs (Snippets A, B, C)
                        y1, y2 = int(h * 0.4), int(h * 0.6)
                        w_third = int(w / 3)
                        
                        snippet_A = img_np[y1:y2, int(w_third * 0.1):int(w_third * 0.9)]
                        snippet_B = img_np[y1:y2, int(w_third * 1.1):int(w_third * 1.9)]
                        snippet_C = img_np[y1:y2, int(w_third * 2.1):int(w_third * 2.9)]
                        
                        # Downscale for performance
                        snippet_A = cv2.resize(snippet_A, (100, 100))
                        snippet_B = cv2.resize(snippet_B, (100, 100))
                        snippet_C = cv2.resize(snippet_C, (100, 100))
                        
                        # State Change Detection
                        combined_np = np.hstack([snippet_A, snippet_B, snippet_C])
                        gray_combined = cv2.cvtColor(combined_np, cv2.COLOR_BGR2GRAY)
                        
                        if previous_state_hash is not None:
                            diff = cv2.absdiff(gray_combined, previous_state_hash)
                            if np.mean(diff) < 5.0:
                                # No significant change, skip this frame
                                time.sleep(1)
                                continue
                                
                        previous_state_hash = gray_combined
                        self.update_label("[color=8A2BE2]State Change Detected!\nOllama is thinking...[/color]")
                        
                        _, encoded = cv2.imencode('.jpg', combined_np)
                        b64_image = base64.b64encode(encoded.tobytes()).decode('utf-8')
                    else:
                        # Fallback if cv2 failed to load
                        self.update_label("[color=8A2BE2]OpenCV missing. Using raw frame...\nOllama is thinking...[/color]")
                        b64_image = base64.b64encode(image_bytes).decode('utf-8')
                        
                    payload = {
                        "model": "deepseek-r1:7b",
                        "prompt": system_instruction + "\nPredict the winning slot.",
                        "images": [b64_image],
                        "stream": False,
                        "options": {"temperature": 0.1}
                    }
                    
                    req = urllib.request.Request("http://localhost:11434/api/generate", data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                    try:
                        with urllib.request.urlopen(req, timeout=45) as response:
                            result = json.loads(response.read().decode())
                            prediction_text = result.get('response', 'No response')
                    except Exception as e:
                        prediction_text = f"Ollama Error: {str(e)}"
                    
                    title = "🔮 Psychic S24"
                    content = prediction_text
                    
                    # Clean up thinking tags from DeepSeek-R1
                    if "</think>" in prediction_text:
                        content = prediction_text.split("</think>")[-1].strip()
                    elif "Ollama Error:" not in prediction_text:
                        content = prediction_text.strip()
                        
                    self.send_notification(title, content)
                    if hasattr(self, 'history_layout'):
                        self.update_history(content)
                        
                    self.update_label(f"[color=00FF00]Local Prediction:[/color]\n[color=8A2BE2]{content}[/color]")
                else:
                    pass 
            except Exception as e:
                self.update_label(f"[color=FF0000]Error in Brain:[/color] {str(e)}")
                if image:
                    try:
                        image.close()
                    except:
                        pass
            
            time.sleep(1)

    @mainthread
    def update_history(self, text):
        from jnius import autoclass
        TextView = autoclass('android.widget.TextView')
        Color = autoclass('android.graphics.Color')
        String = autoclass('java.lang.String')
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        
        # Remove placeholder if it exists
        if self.history_layout.getChildCount() == 1:
            first_child = self.history_layout.getChildAt(0)
            if first_child.getText().toString() == "Waiting for predictions...":
                self.history_layout.removeViewAt(0)
                
        # Add new log entry
        log_text = TextView(context)
        log_text.setText(String(f"[{time.strftime('%H:%M:%S')}] {text}"))
        log_text.setTextColor(Color.WHITE)
        log_text.setPadding(0, 10, 0, 10)
        
        self.history_layout.addView(log_text, 0)
        
        # Keep only the last 25 results
        if self.history_layout.getChildCount() > 25:
            self.history_layout.removeViewAt(25)

    @mainthread
    def update_label(self, text):
        self.label.text = text

if __name__ == '__main__':
    OracleApp().run()