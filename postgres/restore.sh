#!/bin/bash
# postgres/restore.sh

BACKUP_FILE="/backup/pass_cert_backup.sql"

echo "=========================================="
echo "Checking for database backup file..."
echo "=========================================="

# 컨테이너 내부의 /backup 경로에 백업 sql 파일이 실제로 존재하는지 체크
if [ -f "$BACKUP_FILE" ]; then
    echo "🎉 Backup file found! Starting database restoration..."
    
    # pg_dump로 추출한 SQL문을 현재 환경변수로 지정된 DB에 밀어넣음
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$BACKUP_FILE"
    
    echo "✅ Database restoration completed successfully!"
else
    echo "ℹ️ No backup file found at $BACKUP_FILE."
    echo "   Proceeding with default entrypoint configuration."
fi
echo "=========================================="