[app]
title = ASL Mobile App
package.name = aslmobileapp
package.domain = org.aslmobile

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,tflite,txt,md
source.exclude_dirs = tests, bin, .git, .github, __pycache__, .pytest_cache, .venv, buildenv

version = 1.0
requirements = python3,kivy==2.1.0,numpy,pillow,plyer,android

source.main = main.py
orientation = portrait

android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, RECORD_AUDIO, MODIFY_AUDIO_SETTINGS
android.private_storage = False
android.ndk = 25b
android.sdk = 33
android.api = 33
android.minapi = 21
android.enable_androidx = True
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1
