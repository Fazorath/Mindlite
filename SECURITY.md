# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Mindlite, please report it responsibly:

### How to Report
1. **Do not** create a public GitHub issue
2. **Email** the maintainers directly at: security@example.com
3. **Include** detailed information about the vulnerability
4. **Provide** steps to reproduce the issue

### What to Include
- **Description** of the vulnerability
- **Steps** to reproduce
- **Potential impact** assessment
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up

### Response Timeline
- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Resolution**: Within 30 days (depending on complexity)

## Security Considerations

### Data Protection
- **Local storage**: All data is stored locally in SQLite
- **No network access**: Mindlite doesn't connect to external services
- **File permissions**: Database files use standard file permissions

### Input Validation
- **Date parsing**: Validates date formats before processing
- **Command arguments**: Validates all command-line arguments
- **Database queries**: Uses parameterized queries to prevent injection

### Best Practices
- **Keep updated**: Use the latest version
- **File permissions**: Ensure database files have appropriate permissions
- **Backup data**: Regularly export your data
- **Secure environment**: Run in a secure environment

## Security Features

### Built-in Protections
- **Input sanitization**: All user input is validated
- **SQL injection prevention**: Uses parameterized queries
- **File system safety**: Validates file paths and permissions
- **Error handling**: Prevents information leakage

### Recommendations
- **Regular updates**: Keep Mindlite updated
- **Secure backups**: Encrypt exported data if needed
- **Access control**: Use appropriate file permissions
- **Environment security**: Run in a secure environment

## Disclosure Policy

### Coordinated Disclosure
We follow a coordinated disclosure process:
1. **Private report** to maintainers
2. **Investigation** and confirmation
3. **Fix development** and testing
4. **Release** of patched version
5. **Public disclosure** after fix is available

### Credit
Security researchers who responsibly disclose vulnerabilities will be:
- **Credited** in security advisories
- **Listed** in the acknowledgments
- **Thanked** for their contribution

## Contact Information

- **Security email**: security@example.com
- **General contact**: issues@example.com
- **GitHub issues**: For non-security bugs

## Security Updates

Security updates will be announced via:
- **GitHub releases**: Tagged as security updates
- **Release notes**: Detailed information about fixes
- **Email notifications**: For critical vulnerabilities

## Thank You

Thank you for helping keep Mindlite secure! Your responsible disclosure helps protect all users.
