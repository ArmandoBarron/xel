FROM ddomizzi/apache:php

#requierments for the mesh:
COPY ./app/includes /var/www/html/includes
COPY ./app/limbo /var/www/html/limbo
COPY ./app/resources /var/www/html/resources
COPY ./app/.htaccess /var/www/html/.htaccess
COPY ./app/index.php /var/www/html/index.php
RUN chown -R www-data:www-data /var/www/html/limbo
