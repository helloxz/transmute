apk add python3
apk add py3-pip
mkdir -p  /opt/transmute && cdgit /opt/transmute
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt