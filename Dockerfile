FROM python:3.7-buster
WORKDIR /synthpop
COPY . .
ENV PATH="/synthpop:${PATH}"
RUN cd /synthpop && python3 setup.py install
RUN cd /synthpop && chmod +x run.sh
ENTRYPOINT ["run.sh"]

