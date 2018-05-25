FROM python:2.7-alpine

RUN pip install beautifulhue Enum

ENV progdir /hue-daycolors
WORKDIR ${progdir}

ADD src ${progdir}/src
add run.sh ${progdir}/run.sh

VOLUME ${progdir}/config

RUN chmod 777 ${progdir}/run.sh

CMD  cd ${progdir} && ./run.sh