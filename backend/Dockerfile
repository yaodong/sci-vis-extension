FROM ubuntu:17.10

RUN apt-get update -y

RUN apt-get install -y python3 python3-pip supervisor \
    libpq-dev imagemagick mpich libmpfr-dev r-base nginx\
    libssl-dev libcurl4-openssl-dev -y

RUN R -e "chooseCRANmirror(ind=1);install.packages('devtools');require(devtools);install_version('TDA', version='1.4.1');" &&\
    R -e "chooseCRANmirror(ind=1);install.packages('RcppCNPy');"

RUN pip3 install Django==1.11.1 && \
    pip3 install djangorestframework-jsonapi==2.4.0 && \
    pip3 install djangorestframework==3.6.3 && \
    pip3 install django-cors-headers==2.0.0 && \
    pip3 install django-celery-results==1.0.1 && \
    pip3 install django-celery-beat==1.0.1 && \
    pip3 install requests==2.13.0 && \
    pip3 install psycopg2==2.6.2 && \
    pip3 install redis==2.10.5 && \
    pip3 install gunicorn==19.6.0 && \
    pip3 install matplotlib==2.0.0 && \
    pip3 install scipy==0.19.0 && \
    pip3 install sympy==1.0 && \
    pip3 install scikit-learn==0.18.1 && \
    pip3 install django-filter==1.0.4

COPY supervisor.conf /etc/supervisor/conf.d/sci-tda.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY . /srv
WORKDIR /srv
VOLUME /srv/data

EXPOSE 8000

CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
