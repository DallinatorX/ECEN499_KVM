#https://gist.github.com/ChriRas/b9aef9771a97249cb4620e0d6ef538c4
#https://stackoverflow.com/questions/3777301/how-to-call-a-shell-script-from-python-code
#https://unix.stackexchange.com/questions/462670/set-default-profile-for-pulseaudio
echo "--------CHECKING AUDIO SOURCES--------"
pactl list short sources # list current available audio sources
echo "--------CHECKING ACTIVE AUDIO PROFILES--------"
pacmd list-cards | grep 'active profile' # lists active audio profiles
echo "--------SETTING AUDIO DEVICE PROFILE--------"
# set capture card audio device to active
echo "--------TRYING TO SET AUDIO DEVICE 2--------"
pactl set-card-profile 2 input:analog-stereo
echo "--------TRYING TO SET AUDIO DEVICE 3--------"
pactl set-card-profile 3 input:analog-stereo #(try again with 3 if 2 is wrong index)
echo "--------SETTING DEFAULT AUDIO SOURCE--------"
# set default audio source as the capture card
pactl set-default-source alsa_input.usb-ASUS_CU4K30_UVC_UHD_Video_902B001112901002-02.analog-stereo
echo "--------MONITORING AUDIO DEVICE--------"
# load loopback to monitor audio from capture card
pactl load-module module-loopback
# launch sunshine
echo "--------LAUNCHING SUNSHINE--------"
gnome-terminal -x sunshine
