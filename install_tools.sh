LAST_DIR=$PWD

mkdir /setup
cd /setup || return

wget https://github.com/mandiant/capa/releases/download/v6.1.0/capa-v6.1.0-linux.zip -O capa.zip
unzip -o capa.zip -d capa
mkdir -p /application/tools/capa
cp capa/capa /application/tools/capa


cd "$LAST_DIR" || return