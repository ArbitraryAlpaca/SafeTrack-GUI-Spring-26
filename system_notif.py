import platform
import subprocess
from windows_toasts import WindowsToaster, Toast, ToastAudio, ToastDuration, AudioSource

def new_notif(title: str, message: str, type: str) -> None:
    
    if platform.system() == "Windows":
        _notify_windows(title, message, type)
    elif platform.system() == "Darwin":  # macOS
        _notify_darwin(title, message, type)
    elif platform.system() == "Linux":
        _notify_linux(title, message, type)

def _notify_windows(title: str, message: str, type: str) -> None:

    toaster = WindowsToaster('SafeTrack')
    
    new_toast = Toast()
    new_toast.text_fields = [title, message]

    if type.lower() == "alert":
        new_toast.duration = ToastDuration.Long 
        new_toast.audio = ToastAudio(sound = AudioSource.Alarm10, looping=True)

    else:
        new_toast.duration = ToastDuration.Short
        new_toast.audio = ToastAudio(sound = AudioSource.Default, looping=False)

    toaster.show_toast(new_toast)

def _notify_darwin(title: str, message: str, type: str) -> None:\

    if type.lower() == "alert":
        script = f'display alert "{title}" message "{message}" as critical'

    else:
        script = f'display notification "{message}" with title "{title}"'
        
    subprocess.run(['osascript', '-e', script])
    
def _notify_linux(title: str, message: str, type: str) -> None:

    urgency = "critical" if type == "alert" else "normal"
    subprocess.run(['notify-send', '-u', urgency, title, message])