FROM python:3.7.11
LABEL Author="skyking116@163.com"
COPY ./site-packages.tar /usr/local/lib/python3.7/
ENV SITE_DIR=/usr/local/lib/python3.7
RUN mkdir -p /src/app && \
 	tar -xvf $SITE_DIR/site-packages.tar -C $SITE_DIR && \
 	rm -rf $SITE_DIR/site-packages.tar
COPY ./main.py /src/app
WORKDIR /src/app/
EXPOSE 3002
CMD python main.py
