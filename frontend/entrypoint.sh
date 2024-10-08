#!/bin/sh

for file in /usr/share/nginx/html/assets/app.*.js; do
  if [ ! -f $file.tmpl.js ]; then
    cp $file $file.tmpl.js
  fi

  envsubst '$REACT_APP_API_BASE' <$file.tmpl.js >$file
done

nginx -g 'daemon off;'
