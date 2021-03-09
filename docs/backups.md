# Backups

Using https://github.com/django-dbbackup/django-dbbackup for backups.

## Configure

Important environment variables to backup to a custom S3-compliant object storage api.

The gpg key is optional

```
GPG_PUBLIC_KEY_URL=https://thekey.com/pgp_keys.asc
GPG_KEY_NAME=name@example.org

S3_ACCESS=xx
S3_SECRET=xx
S3_ENDPOINT=https://xx.net
S3_BUCKET=xx
S3_REGION=xx
```

## Backup

```
./scripts/backup.sh
```

## Restore Encrypted DB Dump

Download the file from the bucket.
Decrypt it on your device with your secret key.

```bash
gpg -d encrypteddata.psql.gz.gpg > data.psql.gz
```

Put the file to your server in a mounted volume and:

```bash
./scripts/restore_db.sh /backups/data.psql.gz
```

Likewise for encrypted & compressed media folder.
