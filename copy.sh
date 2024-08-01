file_size=
file_size=
file_size=$(stat -c %s "" | numfmt --to=iec-i --suffix=B --format='%.2f')
file_size=$(stat -c %s "$1" | numfmt --to=iec-i --suffix=B --format='%.2f')
