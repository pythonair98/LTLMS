# LTLMS Docker Setup

This document provides instructions for running the Learning and Training License Management System (LTLMS) using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually comes with Docker Desktop)

## Project Structure

```
LTLMS/
├── Dockerfile                 # Django application container
├── docker-compose.yml         # Multi-container orchestration
├── .dockerignore             # Files to exclude from Docker build
├── requirements.txt           # Python dependencies
├── manage.py                 # Django management script
├── LTLMS/
│   ├── settings.py           # Original Django settings
│   ├── settings_docker.py    # Docker-specific settings
│   └── ...
├── mysql/
│   └── init/                 # MySQL initialization scripts
└── README_Docker.md          # This file
```

## Quick Start

1. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Web application: http://localhost:8000
   - Database: localhost:3307 (MySQL)

3. **Stop the containers:**
   ```bash
   docker-compose down
   ```

## Detailed Setup Instructions

### 1. First Time Setup

```bash
# Build and start all services
docker-compose up --build

# In a new terminal, create a superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

### 2. Database Management

The MySQL database is automatically created with the following credentials:
- **Database Name:** ltlms
- **Username:** manager
- **Password:** manger@2025#
- **Host:** db (internal Docker network)
- **Port:** 3306 (internal) / 3307 (external)

### 3. Environment Variables

The following environment variables can be customized in `docker-compose.yml`:

```yaml
environment:
  - DEBUG=True                    # Django debug mode
  - DATABASE_HOST=db             # Database host
  - DATABASE_PORT=3306           # Database port
  - DATABASE_NAME=ltlms          # Database name
  - DATABASE_USER=manager        # Database user
  - DATABASE_PASSWORD=manger@2025# # Database password
```

### 4. Volumes

The following volumes are created:
- `mysql_data`: Persistent MySQL data
- `static_volume`: Django static files
- `media_volume`: User uploaded media files

### 5. Useful Commands

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs web
docker-compose logs db

# Execute commands in the web container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic

# Access MySQL database
docker-compose exec db mysql -u manager -p ltlms

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (WARNING: This will delete all data)
docker-compose down -v
```

## Development Workflow

### Making Code Changes

1. **Edit your code** in your local development environment
2. **Rebuild the container** if you added new dependencies:
   ```bash
   docker-compose up --build
   ```
3. **Restart the web service** for code changes:
   ```bash
   docker-compose restart web
   ```

### Adding New Dependencies

1. **Add the dependency** to `requirements.txt`
2. **Rebuild the container:**
   ```bash
   docker-compose up --build
   ```

### Database Migrations

```bash
# Create new migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

## Production Considerations

For production deployment, consider the following changes:

1. **Security:**
   - Change `DEBUG=False` in environment variables
   - Use strong, unique passwords
   - Set `SECRET_KEY` environment variable
   - Remove `"*"` from `ALLOWED_HOSTS`

2. **Performance:**
   - Use a production WSGI server like Gunicorn
   - Configure proper static file serving
   - Set up a reverse proxy (nginx)

3. **Database:**
   - Use a managed database service
   - Configure proper backups
   - Set up database replication if needed

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :8000
   # Change the port in docker-compose.yml
   ```

2. **Database connection issues:**
   ```bash
   # Check if database is running
   docker-compose ps
   # View database logs
   docker-compose logs db
   ```

3. **Permission issues:**
   ```bash
   # Fix file permissions
   docker-compose exec web chown -R appuser:appuser /app
   ```

4. **Static files not loading:**
   ```bash
   # Collect static files
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f web

# Access container shell
docker-compose exec web bash
```

## File Structure for Docker

- **Dockerfile:** Defines the Django application container
- **docker-compose.yml:** Orchestrates the application and database
- **.dockerignore:** Excludes unnecessary files from the build context
- **LTLMS/settings_docker.py:** Docker-specific Django settings
- **mysql/init/:** Directory for MySQL initialization scripts

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Ensure Docker Desktop is running
3. Verify all ports are available
4. Check the troubleshooting section above

For additional help, refer to the Django and Docker documentation. 