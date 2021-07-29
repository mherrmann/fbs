# Place fpm on the PATH:
export PATH=$PATH:$(ruby -e "puts Gem.user_dir")/bin
PS1='arch:\W$ '

# Display welcome message:
[ ! -z "$TERM" -a -r /etc/motd ] && cat /etc/motd