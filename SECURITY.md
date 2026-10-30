# Security Information

## ✅ Security Measures

### Data Protection
- ✅ **No hardcoded credentials** - All API keys/tokens use environment variables or placeholders
- ✅ **No sensitive data in repo** - `.env`, database files, and logs excluded via `.gitignore`
- ✅ **Local-only storage** - All threat data stored locally in SQLite, never transmitted to cloud
- ✅ **No external APIs required** - Uses only public RSS feeds, no authentication needed

### Code Security
- ✅ **HTML/XSS protection** - All user input sanitized with `escapeHtml()` function
- ✅ **SQL injection prevention** - Uses parameterized queries via SQLite
- ✅ **No eval() or exec()** - No dynamic code execution
- ✅ **No shell execution** - No subprocess calls with user input

### Repository Protection
- ✅ **Project status clearly marked** - See `CONTRIBUTING.md`
- ✅ **Branch protection enabled** - Main branch requires review
- ✅ **No sensitive commits** - Clean history without secrets

### Data Sources
All threat feeds from **trusted security vendors only**:
- Bleeping Computer (established security news)
- HackerNews (community curated)
- Reddit r/netsec (community security discussion)
- SecurityWeek (commercial security news)
- Unit42 Research (Palo Alto threat research)
- Palo Alto Networks Blog (vendor security content)
- CISA KEV (US government vulnerability database)

---

## 📋 Sensitive Data Checklist

### ✅ NOT in repository:
- API keys or tokens
- Database files (*.db)
- Environment variables (.env files)
- Personal information
- Authentication credentials
- Private configuration files

### ✅ Safe to expose:
- RSS feed URLs (all public)
- Code architecture and logic
- Dashboard design
- Threat filtering rules
- Documentation

---

## 🔐 For Personal Use

If you deploy this system:

1. **Set up environment variables:**
   ```bash
   # .env (never commit this!)
   DATABASE_PATH=/secure/path/threats.db
   PORT=8000
   ```

2. **Secure the database:**
   ```bash
   chmod 600 data/threats.db
   chmod 700 data/
   ```

3. **Run on trusted network only:**
   - Dashboard accessible only from your machine/private network
   - Do not expose port 8000 to the internet
   - Use VPN or SSH tunnel if remote access needed

4. **Regular backups:**
   ```bash
   cp data/threats.db backups/threats.db.$(date +%Y%m%d)
   ```

---

## 🚨 Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT create a public issue**
2. **Do NOT fork and commit the fix**
3. **Email privately** with details of the vulnerability
4. Allow time for review before public disclosure

---

## 📚 Dependencies Security

All dependencies are publicly available Python packages:
- `feedparser` - RSS parsing
- `fastapi` - Web framework
- `sqlite3` - Database (built-in)
- `apscheduler` - Task scheduling

No proprietary or closed-source dependencies.

---

**Last Updated:** October 30, 2026

---
