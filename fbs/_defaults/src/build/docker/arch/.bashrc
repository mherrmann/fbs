# Place fpm on the PATH:
export PATH=$PATH:$(ruby -e "puts Gem.user_dir")/bin
PS1='arch:\W$ '
source /root/${app_name}/venv/bin/activate