# 首次运行执行次脚本
# Install the service with systemctl
sudo ln -s /home/pi/smsutil/init_script/smsutil.service /etc/systemd/system

sudo systemctl enable smsutil

sudo systemctl start smsutil