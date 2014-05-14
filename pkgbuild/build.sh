#!/bin/sh

set -e

SCRDIR=$(dirname $(readlink -f $0))

: ${PYTHONDONTWRITEBYTECODE="true"}; export PYTHONDONTWRITEBYTECODE

. $SCRDIR/librc

isnullx DESTDIR
isnullx NAME
isnullx VERSION

execute rsync --exclude-from=$SCRDIR/rsync.exclude -ai $SCRDIR/../ $DESTDIR/

execute virtualenv -q $DESTDIR/env/

{
  . $DESTDIR/env/bin/activate
  execute cd $DESTDIR/

  execute pip install -r requirements/production.txt
  execute ln -sf /etc/$NAME/local.py src/$NAME/settings/local.py
}
