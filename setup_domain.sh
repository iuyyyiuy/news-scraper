#!/bin/bash
# Setup custom domain with SSL
# Run this on your Digital Ocean server after DNS is configured

DOMAIN="your-domain.com"  # Change this to your actual domain

echo "Setting up domain: $DOMAIN"

# Update Nginx configuration
cat > /etc/nginx/sites-available/news-scraper <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # For SSE (Server-Sent Events)
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_read_timeout 3600s;
    }
}
EOF

# Test and reload Nginx
nginx -t && systemctl reload nginx

echo ""
echo "✅ Nginx configured for $DOMAIN"
echo ""
echo "Now install SSL certificate:"
echo "  apt install certbot python3-certbot-nginx -y"
echo "  certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
