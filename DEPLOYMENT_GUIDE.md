# 🚀 راهنمای کامل Deploy کردن ربات جنگ سیاسی روی Zeabur

## 📋 لیست چک قبل از Deploy

### ✅ چک کردن فایل‌های لازم
- [x] `main.py` - کد اصلی ربات
- [x] `Dockerfile` - برای ساخت Docker image
- [x] `pyproject.toml` - dependency ها
- [x] `start.sh` - اسکریپت راه‌اندازی
- [x] `docker-compose.yml` - برای تست local
- [x] `data/` - پوشه داده‌ها
- [x] `.dockerignore` - فایل‌های ignore شده

### ✅ اطلاعات مورد نیاز
- **Bot Token**: `8109322082:AAFBpC7pIJRiLogy_4pvZ8Gd6zQ4W6O74s4`
- **Admin ID**: باید ID تلگرام خودتان را جایگزین کنید

## 🔧 مرحله 1: آماده‌سازی پروژه

### 1.1 دریافت Bot Token
```
1. به @BotFather بروید
2. اگر ربات دارید: /mybots
3. اگر ربات ندارید: /newbot
4. نام ربات: Political War Bot
5. Username: political_war_bot (یا هر نام دیگر)
6. Token را کپی کنید
```

### 1.2 پیدا کردن Admin ID
```
1. به @userinfobot بروید
2. /start کلیک کنید
3. ID خودتان را کپی کنید
4. در main.py جایگزین کنید: ADMIN_ID = YOUR_ID
```

## 🌐 مرحله 2: Deploy روی Zeabur

### 2.1 ساخت حساب کاربری
1. به [zeabur.com](https://zeabur.com) بروید
2. "Sign Up" کلیک کنید
3. با GitHub یا Email ثبت نام کنید
4. Dashboard را باز کنید

### 2.2 ساخت پروژه جدید
1. "Create Project" کلیک کنید
2. نام پروژه: `political-war-bot`
3. Region: `Asia Pacific` (برای ایران بهتر است)
4. "Create" کلیک کنید

### 2.3 اضافه کردن سرویس
```
1. "Add Service" کلیک کنید
2. "Git" انتخاب کنید
3. Repository خود را connect کنید
4. یا فایل‌ها را Drag & Drop کنید
```

### 2.4 تنظیمات Build
```
Runtime: Python
Build Command: pip install python-telegram-bot==21.0
Start Command: python main.py
Port: 8080 (اختیاری)
```

### 2.5 Environment Variables
```
BOT_TOKEN = 8109322082:AAFBpC7pIJRiLogy_4pvZ8Gd6zQ4W6O74s4
ADMIN_ID = YOUR_TELEGRAM_ID
```

## 🚀 مرحله 3: Deploy Process

### 3.1 آپلود فایل‌ها
```bash
# اگر از Git استفاده می‌کنید
git init
git add .
git commit -m "Initial deploy"
git push origin main
```

### 3.2 نظارت بر Build
1. در Zeabur Dashboard، tab "Deploy" را باز کنید
2. Build logs را نظاره کنید
3. باید پیام‌های زیر را ببینید:
   - Installing dependencies...
   - Building Docker image...
   - Starting container...
   - Bot is running!

### 3.3 تایید موفقیت
```
✅ Status: Running
✅ Port: 8080
✅ Logs: "Bot is running and ready to receive commands!"
```

## 🧪 مرحله 4: تست ربات

### 4.1 کامندهای اصلی
```
/start - شروع بازی
/join - پیوستن به حزب
/profile - نمایش پروفایل
/shop - فروشگاه
/help - راهنما
```

### 4.2 کامندهای Admin
```
/addplayer USER_ID - اضافه کردن بازیکن
/removeplayer USER_ID - حذف بازیکن
/listplayers - لیست بازیکنان مجاز
```

### 4.3 تست سیستم جنگ
```
1. /join - پیوستن به حزب
2. /shop - خرید سرباز
3. 🗺️ مدیریت مناطق - انتخاب منطقه
4. ⚔️ حمله - حمله به حزب دیگر
```

## 📊 مرحله 5: مانیتورینگ

### 5.1 مشاهده Logs
```
در Zeabur Dashboard:
1. Service خود را انتخاب کنید
2. Tab "Logs" را باز کنید
3. Real-time logs را مشاهده کنید
```

### 5.2 Metrics مهم
```
- Response Time: کمتر از 1 ثانیه
- Error Rate: کمتر از 1%
- Memory Usage: کمتر از 256MB
- CPU Usage: کمتر از 50%
```

### 5.3 Health Check
```python
# ربات هر 30 ثانیه این پیام را می‌فرستد:
"Bot is running and ready to receive commands!"
```

## 🔧 مرحله 6: Troubleshooting

### 6.1 خطاهای معمول

**خطا: "Bot token is invalid"**
```
❌ مشکل: Bot token اشتباه است
✅ راه حل: Token را از @BotFather دوباره بگیرید
```

**خطا: "Permission denied"**
```
❌ مشکل: مجوز نوشتن در data directory
✅ راه حل: Dockerfile را چک کنید
```

**خطا: "Import error"**
```
❌ مشکل: python-telegram-bot نصب نشده
✅ راه حل: requirements را چک کنید
```

### 6.2 Debug کردن
```bash
# Local test
docker-compose up --build

# Check logs
docker logs political-war-bot

# Interactive shell
docker exec -it political-war-bot /bin/bash
```

### 6.3 مشکلات احتمالی و راه حل

**مشکل: Bot respond نمی‌کند**
```
1. Environment variables را چک کنید
2. Bot token را verify کنید
3. Network connectivity تست کنید
4. Logs را بررسی کنید
```

**مشکل: Data ذخیره نمی‌شود**
```
1. data directory permissions چک کنید
2. File system space بررسی کنید
3. JSON file format validate کنید
```

## 📈 مرحله 7: Scale کردن

### 7.1 Resource Planning
```
کاربران کم (1-100): 
- CPU: 0.25 core
- Memory: 256MB
- Storage: 1GB

کاربران متوسط (100-1000):
- CPU: 0.5 core  
- Memory: 512MB
- Storage: 2GB

کاربران زیاد (1000+):
- CPU: 1 core
- Memory: 1GB
- Storage: 5GB
```

### 7.2 Performance Optimization
```python
# بهینه‌سازی JSON operations
- Use memory caching
- Batch operations
- Async file I/O

# بهینه‌سازی Telegram API
- Use connection pooling
- Implement rate limiting
- Add retry logic
```

## 💾 مرحله 8: Backup & Recovery

### 8.1 Backup Strategy
```
1. Daily backup data files
2. Weekly backup full project
3. Monthly backup to external storage
```

### 8.2 Recovery Plan
```
1. Restore data files
2. Redeploy service
3. Verify functionality
4. Notify users
```

## 🔐 مرحله 9: Security

### 9.1 Environment Security
```
✅ Bot token in environment variables
✅ Admin ID protection
✅ Input validation
✅ Rate limiting
```

### 9.2 Production Tips
```
1. Use proper logging
2. Implement error handling
3. Add monitoring alerts
4. Regular security updates
```

## 🎯 مرحله 10: Go Live!

### 10.1 Final Checklist
```
✅ Bot responds to /start
✅ Users can join parties
✅ Shop system works
✅ Combat system functional
✅ Admin commands work
✅ Logs are clean
✅ Performance is good
```

### 10.2 Launch Steps
```
1. Announce in channel
2. Monitor initial usage
3. Handle user feedback
4. Fix any issues quickly
5. Scale as needed
```

---

## 🎉 تبریک! ربات شما آماده است

شما حالا یک ربات جنگ سیاسی کامل با سیستم منطقه‌ای دارید که روی Zeabur اجرا می‌شود.

### 🔥 ویژگی‌های پیاده‌سازی شده:
- ✅ 6 حزب سیاسی
- ✅ 6 منطقه برای هر حزب  
- ✅ سیستم خرید سرباز و شرکت
- ✅ جابجایی سرباز بین مناطق
- ✅ سیستم جنگ و حمله
- ✅ پاداش‌های اقتصادی
- ✅ رابط کاربری فارسی
- ✅ سیستم مجوز دسترسی

### 💬 برای پشتیبانی:
- GitHub Issues
- Zeabur Documentation
- Telegram Bot API Docs

**موفق باشید! 🚀**