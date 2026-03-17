[app]
# (str) Title of your application
title = S24 Oracle

# (str) Package name
package.name = s24oracle

# (str) Package domain (needed for android/ios packaging)
package.domain = org.psychic

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt

# (str) Application versioning
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,google-genai,jnius

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, FOREGROUND_SERVICE, MEDIA_PROJECTION

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Accept the Android SDK license agreement
android.accept_sdk_license = True

# (str) Android SDK directory
# android.sdk_path = 

# (str) Android NDK directory
# android.ndk_path = 

# (str) Android architectures to build for
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) Android Gradle dependencies
android.gradle_dependencies = androidx.core:core:1.6.0

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
