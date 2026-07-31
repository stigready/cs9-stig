FROM almalinux:10

RUN dnf -y install \
      openscap-scanner \
      scap-security-guide \
      python3 \
      python3-pip \
      sudo \
      which \
      authselect \
    && dnf clean all \
    && python3 -m pip install --no-cache-dir "ansible-core>=2.16,<2.18" PyYAML defusedxml lxml \
    && ansible-galaxy collection install -p /usr/share/ansible/collections community.general ansible.posix

COPY compliance/entrypoint-prove.sh /entrypoint-prove.sh
RUN chmod +x /entrypoint-prove.sh

WORKDIR /role
ENV ANSIBLE_PYTHON_INTERPRETER=/usr/bin/python3
ENV ANSIBLE_COLLECTIONS_PATH=/usr/share/ansible/collections

ENTRYPOINT ["/entrypoint-prove.sh"]
