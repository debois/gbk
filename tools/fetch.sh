#!/bin/sh
# usage: fetch.sh 'filename=2132/MT495GT1450.XML&tournament=495&section=1' WORKDIR
# Downloads the result pages and writes WORKDIR/boards.json and WORKDIR/boards.txt.
set -eu
q=$1; w=$2; t=$(dirname "$(readlink -f "$0")")
mkdir -p "$w/dl"
get() { curl -sfL -A "Mozilla/5.0" -o "$w/dl/$1.html" "https://resultater.bridge.dk/template/$1.php?$q$2"; }
get spilresultater '&round=1&half=1'
for p in startliste resultater pairhacscore; do
  get $p ''
  python3 -I "$t/totext.py" "$w/dl/$p.html" | sed 's/^[ \t]*//' | grep -v '^$' > "$w/$p.txt"
done
python3 -I "$t/totext.py" "$w/dl/spilresultater.html" > "$w/page.txt"
python3 -I "$t/parse.py" "$w/page.txt" "$w/dl/spilresultater.html" "$w/boards.json" > /dev/null
python3 -I "$t/fmt.py" "$w/boards.json" > "$w/boards.txt"
