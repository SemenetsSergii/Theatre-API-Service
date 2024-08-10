# Theatre-API-Service
Dgango rest API for a theatre. Visitors of the Theatre to make Reservations tickets online and choose needed seats.
## Installation

Python3 must be already installed

```shell
git clone https://github.com/SemenetsSergii/Theatre-API-Service.git
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
### For creating new account follow these endpoints:
- Create user - /api/user/register
- Get access token - /api/user/token

You can load ModHeader extension for your browser and add request header (JWT). Example:

Opera: https://addons.opera.com/ru/extensions/details/modheader/
Chrome: https://chromewebstore.google.com/detail/modheader-modify-http-hea/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=ru&pli=1

- key: Authorization

- value: Bearer 

### Environment Variables Setup

1. Create a `.env` file in the root directory of your project.
2. Add the following key-value pairs to the `.env` file. Example:

```shell
DB_HOST=<your-db-host>
DB_NAME=<your-db-name>
DB_USER=<your-db-user>
DB_PASSWORD=<your-db-password>
DB_PORT=<your-db-port>
```
### Run with docker

Docker should be installed

```bash
   docker-compose build
   docker-compose up
```
## Features
- JWT authenticated
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing reservations ant tickets
- Creating plays with genres and actors
- Creating theatre halls
- Adding performances
- Filtering plays and performances

![Website Interface](/Theatre_demo.jpg))
![Website Structure](/theatre_structure.jpg)