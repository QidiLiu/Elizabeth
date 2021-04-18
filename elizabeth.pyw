import threading
import time
import psutil
import pyinotify
import os

"System background assistant"

__author__ = 'QidiLiu'

KICAD_RUNNING = False # Check if KiCad is running
NEW_LIB = '/home/qidi/Documents/KiCad_Lib/new_lib'

def kicad_monitor():
    global KICAD_RUNNING
    while True:
        proc_iter = psutil.process_iter(attrs=["pid", "name", "cmdline"])
        KICAD_RUNNING = any("kicad" in p.info["cmdline"] for p in proc_iter)
        time.sleep(1)

def library_reader():
    global KICAD_RUNNING, NEW_LIB
    
    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_MOVED_TO(self, event):
            if(event.name.split('.')[-1] == 'zip'):
                os.system(f'unzip {event.pathname} -d /home/qidi/Documents/KiCad_Lib/new_lib')
                os.system(f'rm {event.pathname}')
                for root, dirs, files in os.walk(NEW_LIB):
                    for file in files:
                        if file.endswith(".stp"):
                             stp_file = os.path.join(root, file)

                # Find kicad folder
                for root, dirs, files in os.walk(NEW_LIB):
                    for dir in dirs:
                        if(dir == 'KiCad'):
                             kicad_dir = os.path.join(root, dir)

                for root, dirs, files in os.walk(kicad_dir):
                    for file in files:
                        if file.endswith(".kicad_mod"):
                             kicad_mod_file = os.path.join(root, file)
                        if file.endswith(".lib"):
                             lib_file = os.path.join(root, file)

                # Write new .lib to my_lib.lib
                with open(lib_file, 'r') as new_lib_file:
                    new_contents = new_lib_file.read()

                with open('/home/qidi/Documents/KiCad_Lib/my_lib.lib', 'a') as file:
                    file.write(new_contents)
                os.system(f'cp {stp_file} /home/qidi/Documents/KiCad_Lib/my_lib.3dshapes')
                os.system(f'cp {kicad_mod_file} /home/qidi/Documents/KiCad_Lib/my_lib.pretty')
                os.system('rm -rf /home/qidi/Documents/KiCad_Lib/new_lib/*')

    while True:
        if(KICAD_RUNNING):
            wm = pyinotify.WatchManager()
            handler = EventHandler()
            notifier = pyinotify.ThreadedNotifier(wm, handler)
            notifier.start()
            wm.add_watch('/home/qidi/Downloads', pyinotify.IN_MOVED_TO)
            # It'll be stoped when KICAD_RUNNING is False
            while KICAD_RUNNING:
                time.sleep(1)
            notifier.stop()
        else:
            time.sleep(1)

def main():
    kicad_monitor_thread = threading.Thread(target=kicad_monitor)
    library_reader_thread = threading.Thread(target=library_reader)
    kicad_monitor_thread.start()
    library_reader_thread.start()

if __name__ == "__main__":
    main()

