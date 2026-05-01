# Database Monitoring & Auto-Recovery System

A production-grade PostgreSQL monitoring and auto-recovery system built for CERN database operations.

## 🚀 Features

### Core Monitoring
- **Real-time Health Checks**: Continuous monitoring of PostgreSQL primary and replica instances
- **Advanced Metrics**: Connection tracking, query performance, replication lag, resource utilization
- **Prometheus Integration**: Full metrics export for external monitoring systems

### Auto-Recovery
- **Intelligent Failure Detection**: Automatic detection of database failures and performance issues
- **Automated Recovery**: Self-healing capabilities with configurable retry limits
- **Recovery Logging**: Complete audit trail of all recovery actions

### Alerting
- **Slack Integration**: Real-time alerts to Slack channels
- **Multi-level Alerts**: Critical, warning, and informational alert categories
- **Alert Cooldown**: Configurable cooldown periods to prevent alert spam

### Dashboard
- **React Frontend**: Modern, responsive web interface
- **Real-time Updates**: Live monitoring data with automatic refresh
- **Grafana Integration**: Advanced visualization dashboards

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │   PostgreSQL    │
│   (Port 3001)   │◄──►│   (Port 8000)   │◄──►│   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Prometheus    │
                       │   (Port 9090)   │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Grafana       │
                       │   (Port 3000)   │
                       └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Primary database with replication
- **Prometheus**: Metrics collection and storage
- **AsyncPG**: High-performance async PostgreSQL driver

### Frontend
- **React 18**: Modern UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Data visualization library
- **Lucide React**: Icon library

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Grafana**: Advanced dashboards
- **AlertManager**: Alert routing and management

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd cern-db
```

2. **Configure environment**
```bash
cp src/backend/.env.example src/backend/.env
# Edit .env with your configuration
```

3. **Start the system**
```bash
docker-compose up -d
```

4. **Access the applications**
- **Frontend Dashboard**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090

## 📊 Monitoring Features

### Health Checks
- Database connectivity monitoring
- Connection pool status
- Replication lag tracking
- Resource utilization monitoring

### Metrics Collection
- Active connections
- Query performance
- Database size
- CPU and memory usage
- Replication status

### Auto-Recovery Actions
- Automatic database restart
- Connection pool reset
- Replica promotion
- Recovery attempt logging

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://admin:admin123@postgres-primary:5432/monitoring_db
REPLICA_URL=postgresql://admin:admin123@postgres-replica:5432/monitoring_db

# Monitoring Configuration
MONITOR_INTERVAL=30
HEALTH_CHECK_INTERVAL=10
AUTO_RECOVERY_ENABLED=true

# Alert Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
ALERT_COOLDOWN=300

# Thresholds
MAX_CONNECTIONS=100
SLOW_QUERY_THRESHOLD=1.0
CPU_THRESHOLD=80.0
REPLICATION_LAG_THRESHOLD=10.0
```

### Prometheus Configuration

The system automatically configures Prometheus with:
- PostgreSQL exporter metrics
- Custom application metrics
- Alert rules for common issues

### Grafana Dashboards

Pre-configured dashboards include:
- Database overview
- Performance metrics
- Recovery actions
- Alert history

## 🚨 Alerting

### Alert Types
- **Database Down**: Critical alert when database becomes unavailable
- **High Connections**: Warning when connection count approaches limit
- **Slow Queries**: Warning for performance degradation
- **Replication Lag**: Warning for replication delays
- **Recovery Actions**: Info alerts for recovery attempts

### Slack Integration

Configure Slack alerts by setting the `SLACK_WEBHOOK_URL` environment variable. The system will send:
- Critical alerts to `#db-alerts-critical`
- Warning alerts to `#db-alerts-warning`
- General alerts to `#db-alerts`

## 🔄 Recovery System

### Automatic Recovery
The system automatically attempts recovery when:
- Database connection fails
- Performance thresholds are exceeded
- Replication lag exceeds limits

### Recovery Actions
- Database service restart
- Connection pool reset
- Replica promotion
- Configuration reload

### Recovery Limits
- Maximum 3 recovery attempts per failure
- 5-minute cooldown between attempts
- Manual override available through dashboard

## 📈 API Endpoints

### Health Endpoints
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health status
- `POST /api/v1/health/check` - Force health check

### Monitoring Endpoints
- `GET /api/v1/monitoring/status` - Monitoring status
- `GET /api/v1/monitoring/metrics` - Current metrics
- `GET /api/v1/monitoring/database/stats` - Database statistics

### Recovery Endpoints
- `GET /api/v1/recovery/status` - Recovery status
- `POST /api/v1/recovery/trigger` - Manual recovery trigger
- `GET /api/v1/recovery/history` - Recovery history

## 🧪 Testing

### Test Failure Simulation
```bash
# Simulate database failure
curl -X POST http://localhost:8000/api/v1/monitoring/test/failure \
  -H "Content-Type: application/json" \
  -d '{"db_type": "primary"}'
```

### Test Alerts
```bash
# Test alert system
curl -X POST http://localhost:8000/api/v1/recovery/test-alert \
  -H "Content-Type: application/json" \
  -d '{"alert_type": "database_down", "message": "Test alert"}'
```

## 📊 Performance

### System Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 20GB storage
- **Recommended**: 4 CPU cores, 8GB RAM, 50GB storage

### Monitoring Overhead
- **CPU Usage**: < 5% overhead
- **Memory Usage**: < 500MB additional memory
- **Network**: Minimal bandwidth usage

## 🔒 Security

### Authentication
- API endpoints secured with configurable authentication
- Database connections use encrypted passwords
- Environment-based configuration management

### Network Security
- Internal container communication
- Configurable external access
- SSL/TLS support for external connections

## 🛠️ Development

### Local Development
```bash
# Backend development
cd src/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend development
cd src/frontend
npm install
npm start
```

### Code Structure
```
src/
├── backend/
│   ├── app/
│   │   ├── core/          # Core functionality
│   │   ├── api/routes/    # API endpoints
│   │   └── models/        # Data models
│   └── main.py           # Application entry
└── frontend/
    ├── src/
    │   ├── components/    # React components
    │   ├── pages/         # Page components
    │   └── services/      # API services
    └── public/           # Static assets
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboards**: http://localhost:3000
- **Prometheus Metrics**: http://localhost:9090/metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the Grafana dashboards

## 🎯 Production Deployment

### Docker Production
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Configuration
- Set production environment variables
- Configure external database connections
- Set up proper SSL certificates
- Configure backup strategies

### Monitoring Setup
- Configure external Prometheus instance
- Set up Grafana with persistent storage
- Configure AlertManager routing
- Set up log aggregation

---

**Built for CERN Database Operations** 🚀
