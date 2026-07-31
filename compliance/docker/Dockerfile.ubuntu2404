FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      openscap-scanner \
      ssg-base \
      ssg-nvidia \
      ssg-debderived \
      ssg-ubuntu2404 \
      python3 \
      python3-pip \
      sudo \
      ansible \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir --break-system-packages PyYAML defusedxml lxml \
    && ansible-galaxy collection install -p /usr/share/ansible/collections community.general ansible.posix

COPY compliance/entrypoint-prove.sh /entrypoint-prove.sh
RUN chmod +x /entrypoint-prove.sh

WORKDIR /role
ENV ANSIBLE_PYTHON_INTERPRETER=/usr/bin/python3
ENV ANSIBLE_COLLECTIONS_PATH=/usr/share/ansible/collections

ENTRYPOINT ["/entrypoint-prove.sh"]
