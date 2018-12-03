PS1='fedora:\W$ '
source /root/${app_name}/venv/bin/activate
# Display welcome message:
[ ! -z "$TERM" -a -r /etc/motd ] && cat /etc/motd