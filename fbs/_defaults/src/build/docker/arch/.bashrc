# Place fpm on the PATH:
export PATH=$PATH:$(ruby -e "puts Gem.user_dir")/bin
PS1='arch:\W$ '
source /root/${app_name}/venv/bin/activate
# Display welcome message:
[ ! -z "$TERM" -a -r /etc/motd ] && cat /etc/motd