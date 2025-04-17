FROM nginxinc/nginx-unprivileged:1.24.0-alpine

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./uwsgi_params /etc/nginx/uwsgi_params

USER root
RUN mkdir -p /vol/web/static/ && mkdir -p /vol/web/media/
RUN chmod 755 /vol/web/static/
RUN chmod 755 /vol/web/media/

USER nginx