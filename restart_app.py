import subprocess

print "Run restart script"
cmd =r"sh /app/raspberry_pi_wifi_counting/restart_app.sh"
subprocess.Popen(cmd, shell=True)
