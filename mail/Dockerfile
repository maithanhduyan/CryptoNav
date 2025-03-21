FROM Ubuntu:24.04 as development
RUN apt-get update && apt-get install -y \
  python3 \
  postfix \
  dovecot \
  apache2 \
  php8.3 \
  php8.3-pgsql \
  roundcube \
  mailutils
COPY config.inc.php.tpl /etc/roundcube/config.inc.php.tpl
# Cấu hình Postfix, Dovecot, và Roundcube (các lệnh cụ thể cần tham khảo tài liệu)
CMD ["sh", "-c", "cp /etc/roundcube/config.inc.php.tpl /etc/roundcube/config.inc.php && \
  sed -i 's|{{DB_USER}}|${DB_USER}|g' /etc/roundcube/config.inc.php && \
  sed -i 's|{{DB_PASSWORD}}|${DB_PASSWORD}|g' /etc/roundcube/config.inc.php && \
  sed -i 's|{{DB_HOST}}|${DB_HOST}|g' /etc/roundcube/config.inc.php && \
  sed -i 's|{{DB_NAME}}|${DB_NAME}|g' /etc/roundcube/config.inc.php && \
  service postfix start && service dovecot start && apache2 -D FOREGROUND"]

FROM Ubuntu:24.04 as production
RUN apt-get update && apt-get install -y \
  postfix \
  dovecot \
  apache2 \
  php8.3 \
  php8.3-pgsql \
  roundcube
COPY --from=development /etc/postfix /etc/postfix
COPY --from=development /etc/dovecot /etc/dovecot
COPY --from=development /etc/roundcube /etc/roundcube
COPY --from=development /etc/roundcube/config.inc.php.tpl /etc/roundcube/config.inc.php.tpl
CMD ["sh", "-c", "cp /etc/roundcube/config.inc.php.tpl /etc/roundcube/config.inc.php && \
  sed -i 's|{{DB_USER}}|${DB_USER}|g' /etc/roundcube/config.inc.php && \
  sed -i 's|{{DB_PASSWORD}}|${DB_PASSWORD}|g' /etc/roundcube/config.inc.php && \
  sed -i 's|{{DB_HOST}}|${DB_HOST}|g' /etc/roundcube/config.inc.php && \
  sed -i 's|{{DB_NAME}}|${DB_NAME}|g' /etc/roundcube/config.inc.php && \
  service postfix start && service dovecot start && apache2 -D FOREGROUND"]