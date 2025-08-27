# 🚀 Quilty App - Simple Production Deployment

This guide provides simple scripts to deploy your Lolita application from `/home/dwood/lolita` to production at `quilty.app`.

## 📋 Available Scripts

### 1. Full Production Deployment
```bash
./deploy-to-production.sh
```
**Use this for:** New features, dependency changes, major updates

**What it does:**
- ✅ Creates backup of current production
- ✅ Stops production services
- ✅ Syncs all files (excluding node_modules, logs, etc.)
- ✅ Installs/updates dependencies
- ✅ Builds frontend
- ✅ Restarts services
- ✅ Performs health checks
- ✅ Auto-rollback on failure

### 2. Quick Deploy (Fast Updates)
```bash
./quick-deploy.sh
```
**Use this for:** Small code changes, bug fixes, content updates

**What it does:**
- ⚡ Syncs only source files (no dependency install)
- ⚡ Restarts services
- ⚡ Quick health check
- ⚡ Much faster than full deployment

### 3. Rollback to Previous Version
```bash
./rollback-production.sh
```
**Use this for:** Emergency recovery, reverting bad deployments

**What it does:**
- 🔄 Finds most recent backup
- 🔄 Restores all files
- 🔄 Reinstalls dependencies
- 🔄 Rebuilds and restarts

## 🎯 Recommended Workflow

### For Development Changes
1. Make changes in `/home/dwood/lolita`
2. Test locally
3. Deploy to production:
   ```bash
   cd /home/dwood/lolita
   ./deploy-to-production.sh
   ```

### For Quick Fixes
1. Make small changes in `/home/dwood/lolita`
2. Quick deploy:
   ```bash
   cd /home/dwood/lolita
   ./quick-deploy.sh
   ```

### If Something Goes Wrong
```bash
cd /home/dwood/lolita
./rollback-production.sh
```

## 🔒 Safety Features

- **Automatic Backups**: Every deployment creates a timestamped backup
- **Health Checks**: Verifies services are running after deployment
- **Auto-Rollback**: Full deployment rolls back automatically on failure
- **File Exclusions**: Doesn't overwrite logs, uploads, or generated files
- **Permission Management**: Sets proper file permissions

## 📁 What Gets Synced

### ✅ Included
- Source code (`src/`)
- Python services (`python-ai-service/*.py`)
- Configuration files (`package.json`, `svelte.config.js`, etc.)
- Static assets (`static/`)
- Database migrations (`.sql` files)

### ❌ Excluded
- `node_modules/` (reinstalled during deployment)
- `python-ai-service/venv/` (preserved in production)
- Log files (`*.log`)
- Process IDs (`*.pid`)
- User uploads (`uploads/`)
- Generated posters (`static/posters/`)
- Database files (`screenplay_analysis.db`)
- Git history (`.git/`)

## 🔍 Monitoring

After deployment, check:
- 🌐 **Website**: https://quilty.app
- 📚 **API Docs**: https://quilty.app/api/docs
- ❤️ **Health Check**: https://quilty.app/api/auth/me

## 🆘 Troubleshooting

### Deployment Failed
1. Check the error message
2. Look at logs: `/var/log/quilty-*.log`
3. Try rollback: `./rollback-production.sh`

### Services Won't Start
1. Check if ports are in use: `netstat -tlnp | grep -E '(8002|5174)'`
2. Kill stuck processes: `pkill -f uvicorn; pkill -f node`
3. Try manual start: `cd /var/www/vhosts/quilty.app/lolita && ./start-production.sh`

### Permission Issues
```bash
sudo chown -R www-data:www-data /var/www/vhosts/quilty.app/lolita
sudo chmod -R 755 /var/www/vhosts/quilty.app/lolita
```

## 📝 Backup Management

- Backups are stored in `/tmp/quilty-production-backup-TIMESTAMP/`
- Old backups are automatically cleaned up (keeps last 5)
- Manual backup: `rsync -av /var/www/vhosts/quilty.app/lolita/ /tmp/manual-backup/`

## 🎉 That's It!

Your deployment is now as simple as:
```bash
cd /home/dwood/lolita
./deploy-to-production.sh
```

The scripts handle all the complexity for you! 🚀
