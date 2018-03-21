FROM ubuntu:17.10

RUN apt-get update -y && apt-get install -y python3 python3-pip nodejs npm libpq-dev supervisor vim

COPY api/requirements.txt /root/

WORKDIR /root/
RUN pip3 install -r requirements.txt

COPY etc/supervisor/sci-tda.conf /etc/supervisor/conf.d/

RUN apt-get install imagemagick mpich -y

# install R
RUN apt-get install libgmp3-dev libmpfr-dev r-base -y

EXPOSE 8080 8081

CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
