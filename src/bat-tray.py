import pygtk, gobject, os;
pygtk.require("2.0")
import gtk, egg.trayicon

class UpdateTimer:

    bat_present = False;
    
    path_energy_now = None
    path_energy_full = None
    path_current_now = None
    path_status = None
    
    def __init__(self, timeout):
        # look for battery
        self.bat_present = self.lookup_battery()

        # create tray icon
        tray_icon = egg.trayicon.TrayIcon("Battery")
        self.label = gtk.Label()
        self.label.use_markup = True
        tray_icon.add(self.label)
        tray_icon.show_all()
        
        # register a timer
        gobject.timeout_add_seconds(timeout, self.timer_callback)
        self.timer_callback()


    def timer_callback(self):

        if not self.bat_present:
            self.label.set_markup('<span color="#ff0000">No battery</span>')
            # todo stop timer if possible
            return True

        #out = ' <span color="#'

        template_bat = ' <span color="{0}">Bat:</span> <span color="#cfd8dc">{1}{2}</span>'

        with open(self.path_energy_now, "r") as f:
            energy_now = int(f.read())
        f.closed

        with open(self.path_energy_full, "r") as f:
            energy_full = int(f.read())
        f.closed

        if not self.path_status:
            status = None
        else:
            with open(self.path_status, "r") as f:
                status = f.read()
            f.closed

        if not status:
            color = '#ffeb3b'
        elif status == "Charging\n":
            color = '#00ff00'
        elif status == "Discharging\n":
            color = '#ff0000'
        elif status == "Full\n":  
            color = '#00ff00'
        else:
            # in my case it's "Unknown" but actually it is "Charging"
            color = '#00ff00'
        
        time_str = ""
        percentage_str = ""

        if status == "Full\n":
            percentage_str = "Full"
        else:
            percentage = round(100.0 * energy_now / energy_full)
            percentage = int(percentage)
            percentage_str = '{0}%'.format(percentage)            

            if self.path_current_now:
                with open(self.path_current_now, "r") as f:
                    current_now = int(f.read())
                f.closed
            else:
                current_now = None

            if (current_now and current_now > 0):
                if status == "Discharging\n":
                    seconds = int(3600 * energy_now / current_now)
                elif status:
                    seconds = int(3600 * (energy_full - energy_now) / current_now)
                else:
                    seconds = None

                if (seconds):
                    time_template = '{0}:{1}'
                    hours = int(seconds / 3600)
                    seconds -= 3600 * hours
                    minutes = int(seconds / 60)
                    seconds -= 60 * minutes
                    
                    if (hours < 10):
                        h = ' 0' + str(hours)
                    else:
                        h = ' ' + str(hours)
                    if (minutes < 10):
                        m = '0' + str(minutes)
                    else:
                        m = str(minutes)

                    time_str = time_template.format(h,m)

        out = template_bat.format(color, percentage_str, time_str);
        self.label.set_markup(out)

        return True
    
    def lookup_battery(self):
        bat_present = False
        path = "/sys/class/power_supply/"
        dirs = os.listdir(path)
        for dirname in dirs:
            if not dirname.startswith("BAT"):
                continue
            else:
                path = path + dirname
                bat_present = True        
                break
                       
        if not bat_present:
            return False
        else: 
            if os.path.isfile(path + "/energy_now"):
                self.path_energy_now = path + "/energy_now"
                self.path_energy_full = path + "/energy_full"
            elif os.path.isfile(path + "/charge_now"):
                self.path_energy_now = path + "/charge_now"
                self.path_energy_full = path + "/charge_full"
            else:
                print "energy_* or charge_* not found"
                return False

            if os.path.isfile(path + "/power_now"):
                self.path_curent_now = path + "/power_now"
                print "current_now OK" 
            elif os.path.isfile(path + "/current_now"):
                self.path_current_now = path + "/current_now"
                print "current_now OK" 
            else:
                # missing this file is not critical but unpleasant   
                print "current_now or power_now not found"

            if os.path.isfile(path + "/status"):
                self.path_status = path + "/status"
                print "status OK"
            else:
                print "status not found"

            return True
        

if __name__ == '__main__':
    timer = UpdateTimer(20) # sets 20 second update interval
    gtk.main()


