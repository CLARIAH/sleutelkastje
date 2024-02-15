#!/bin/bash

# maak todo app
curl -u 'sysop:striktgeheim' --request POST --url 'https://sleutelkast.sd.di.huc.knaw.nl/add/appl=todo,cred=ookgeheim,redir=test'

# geef todo een functioneel beheerder
curl -u 'sysop:striktgeheim'  --request POST --url 'https://sleutelkast.sd.di.huc.knaw.nl/todo/func,eptid=fcd870170b257be28d04acf3586e5d28a2f4201c'

# genereer een invite in de browser (functioneel beheerder moet inloggen)
https://sleutelkast.sd.di.huc.knaw.nl/invite/todo/foobar

# gebruiker registreer zichzelf via de invite
https://sleutelkast.sd.di.huc.knaw.nl/register/foobar

# gebruiker haalt todo op met API key
./api.sh 'huc:39%E}Pi,p"2#ERA~'

# gebruiker haalt todo op in de browser (na login)
https://todo.sd.di.huc.knaw.nl/todo