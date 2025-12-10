# VAMPIRE - Penetration Testing Management System

A comprehensive Django-based platform for managing security assessments, penetration testing projects, and vulnerability tracking. VAMPIRE streamlines the entire penetration testing workflow from project planning to report generation.

## 🎯 Overview

VAMPIRE is designed for security teams and penetration testers who need to:
- Manage multiple penetration testing projects
- Track security findings with SLA compliance
- Generate professional PDF and Word reports
- Maintain a reusable vulnerability knowledge base
- Monitor project performance and deadlines

## ✨ Features

### 📦 Product Management
- Create and manage products with logos and descriptions
- Organize projects by product
- Track security assessments per product

### 📊 Project Management
- Full project lifecycle management (Planned → In Progress → Completed → On Hold)
- **Schedule Performance Index (SPI)** calculation
  - Automatically tracks if projects are on time or delayed
  - Formula: `SPI = Planned Duration / Actual Duration`
  - Visual indicators: 🟢 On time (SPI ≥ 1) | 🔴 Delayed (SPI < 1)
- Project scope and description tracking
- Date management (start, end, completion dates)

### 🔍 Findings Management
- Comprehensive vulnerability tracking
- **Severity levels**: Low, Medium, High, Critical
- **SLA Tracking** with automatic compliance monitoring:
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 60 days
- Status tracking: Open, Closed, Risk Acceptance
- Proof of Concept (PoC) documentation
- CVSS score support
- Automatic late finding detection
- Delay calculation in days

### 📚 Vulnerability Knowledge Base (VKB)
- Reusable vulnerability templates
- **8 Standard Categories**:
  - Injection-Based Vulnerabilities
  - Authentication & Session Flaws
  - Access Control Issues
  - Security Misconfigurations
  - Data Exposure & Cryptographic Failures
  - Web & API-Specific Vulnerabilities
  - Memory & Low-Level Vulnerabilities
  - Other Notable Vulnerabilities
- Reference VKB entries when creating findings
- Save custom findings to VKB for future use

### 👥 Team & Stakeholder Management
- **Team Assignments**: Assign team members to projects with roles
- **Stakeholder Tracking**: Manage client contacts per project
- Project member visibility in reports

### 📄 Professional Report Generation
- **Multiple Formats**: PDF and DOCX (Word)
- **Background Processing**: Asynchronous report generation
- **Comprehensive Sections**:
  1. Cover Page
  2. Document Details
  3. Scope
  4. Project Members
  5. Stakeholders
  6. Methodology (OWASP-based)
  7. Executive Summary
  8. Finding Summary
  9. Detailed Findings
- **Report History**: Track all generated reports
- Download and delete functionality
- Timestamped filenames

## 🛠️ Technologies Used

- **Framework**: Django 5.2.3
- **Database**: SQLite (development)
- **PDF Generation**: xhtml2pdf (pisa)
- **Word Generation**: python-docx
- **Language**: Python 3.13
- **Template Engine**: Django Templates

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd vampire
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install django==5.2.3
pip install xhtml2pdf
pip install python-docx
```

Or create a `requirements.txt` and install:

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 📁 Project Structure

```
vampire/
├── assignments/          # Team assignment management
├── findings/            # Vulnerability findings
├── products/            # Product management
├── projects/            # Project management
├── reports/             # Report generation
│   └── sections/        # Report section modules
├── stakeholders/        # Stakeholder management
├── vkb/                 # Vulnerability Knowledge Base
├── vampire/             # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/               # Uploaded files (logos, reports)
├── db.sqlite3           # SQLite database
└── manage.py            # Django management script
```

## 🔧 Configuration

### Settings

Key settings in `vampire/settings.py`:

- **SECRET_KEY**: Change in production (use environment variables)
- **DEBUG**: Set to `False` in production
- **ALLOWED_HOSTS**: Add your domain in production
- **MEDIA_ROOT**: Directory for uploaded files
- **MEDIA_URL**: URL prefix for media files

### Environment Variables (Recommended for Production)

```python
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

## 📖 Usage Guide

### 1. Create a Product

Navigate to `/products/` and create a new product with name, logo, and description.

### 2. Create a Project

- Go to `/projects/` or create from product detail page
- Fill in project details:
  - Project name
  - Description and scope
  - Select product
  - Set start and end dates
  - Choose status

### 3. Assign Team Members

- From project detail page, click "Assign New User"
- Select user and assign a role/title

### 4. Add Stakeholders

- From project detail page, click "Add Stakeholder"
- Enter name, email, and position

### 5. Create Findings

- Navigate to project detail page
- Click "Add Finding"
- Fill in:
  - Title, description, impact, recommendation
  - Severity level
  - Affected systems
  - Optional: Reference VKB entry or save to VKB
- System automatically tracks SLA compliance

### 6. Generate Reports

- From project detail page
- Click "Generate PDF" or "Generate Word"
- Report generates in background
- Download when status shows "Done"

## 🔍 Key Metrics

### Schedule Performance Index (SPI)

The SPI is automatically calculated for each project:

- **SPI ≥ 1**: Project is on time or ahead of schedule 🟢
- **SPI < 1**: Project is delayed 🔴

Formula: `SPI = Planned Duration / Actual Duration`

### SLA Compliance

Findings are automatically monitored for SLA compliance:

- System flags findings that exceed their SLA deadline
- Shows delay in days
- Visual indicators in finding lists

## 🗄️ Database Models

### Core Models

- **Product**: Products being tested
- **Project**: Penetration testing projects
- **Finding**: Security vulnerabilities
- **VulnerabilityKnowledgeBase**: Reusable vulnerability templates
- **Assignment**: Team member assignments
- **Stakeholder**: Client contacts
- **ReportHistory**: Generated report tracking

## 🔒 Security Considerations

⚠️ **Important**: Before deploying to production:

1. Change `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Set up proper database (PostgreSQL recommended for production)
6. Configure static file serving
7. Enable HTTPS
8. Review and harden security settings

## 🧪 Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Report generation runs synchronously in background threads (consider using Celery for production)
- SQLite database is suitable for development only (use PostgreSQL for production)

## 🔮 Future Enhancements

- [ ] REST API endpoints
- [ ] Advanced reporting with charts and graphs
- [ ] Email notifications for SLA breaches
- [ ] Integration with vulnerability scanners
- [ ] Dashboard with analytics
- [ ] Export functionality (CSV, Excel)
- [ ] Multi-language support
- [ ] Advanced search and filtering

## 📞 Support

For issues, questions, or contributions, please open an issue on the repository.

## 🙏 Acknowledgments

- OWASP Testing Guide for methodology standards
- Django community for the excellent framework
- All contributors and users of this project

---

**VAMPIRE** - Making penetration testing management easier, one project at a time. 🧛

