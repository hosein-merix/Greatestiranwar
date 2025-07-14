# راهنمای Deploy کردن ربات روی Zeabur

## مرحله 1: آماده‌سازی پروژه

### 1.1 فایل‌های لازم
پروژه شما شامل این فایل‌ها هست:
- `main.py` - کد اصلی ربات
- `Dockerfile` - برای build کردن image
- `runtime.txt` - نسخه Python
- `data/` - پوشه داده‌ها
- `pyproject.toml` - dependency ها

### 1.2 توکن ربات
1. به @BotFather در تلگرام بروید
2. توکن ربات خود را کپی کنید
3. توکن شما: `8109322082:AAFBpC7pIJRiLogy_4pvZ8Gd6zQ4W6O74s4`

## مرحله 2: Deploy روی Zeabur

### 2.1 ساخت پروژه
1. به [zeabur.com](https://zeabur.com) بروید
2. حساب کاربری بسازید (با GitHub یا Email)
3. "Create Project" کلیک کنید
4. اسم پروژه: `political-war-bot`

### 2.2 اضافه کردن سرویس
1. "Add Service" کلیک کنید
2. "Git" انتخاب کنید
3. Repository خود را connect کنید
4. یا از "Deploy from GitHub" استفاده کنید

### 2.3 تنظیمات Environment Variables
در قسمت Environment Variables این متغیرها را اضافه کنید:

```
BOT_TOKEN=8109322082:AAFBpC7pIJRiLogy_4pvZ8Gd6zQ4W6O74s4
ADMIN_ID=123456789
```

**مهم**: `ADMIN_ID` را با ID تلگرام خودتان عوض کنید

### 2.4 Build Settings
1. Runtime: `Python`
2. Build Command: `pip install python-telegram-bot==21.0`
3. Start Command: `python main.py`

## مرحله 3: مراحل Deploy

### 3.1 Push کردن کد
اگر از GitHub استفاده می‌کنید:
```bash
git add .
git commit -m "Deploy to Zeabur"
git push origin main
```

### 3.2 نظارت بر Deploy
1. در Zeabur dashboard، logs را چک کنید
2. باید پیام "Bot is running" را ببینید
3. اگر خطا داشت، logs را بخوانید

## مرحله 4: تست ربات

### 4.1 کامندهای تست
در تلگرام این کامندها را امتحان کنید:
- `/start` - شروع بازی
- `/join` - پیوستن به حزب
- `/profile` - نمایش پروفایل
- `/shop` - فروشگاه
- `/help` - راهنما

### 4.2 Admin Commands
- `/addplayer USER_ID` - اضافه کردن بازیکن
- `/removeplayer USER_ID` - حذف بازیکن
- `/listplayers` - لیست بازیکنان

## مرحله 5: مدیریت داده‌ها

### 5.1 فایل‌های JSON
- `data/players.json` - اطلاعات بازیکنان
- `data/parties.json` - اطلاعات احزاب
- `data/authorized_players.json` - بازیکنان مجاز

### 5.2 Persistence
داده‌ها در فایل‌های JSON ذخیره می‌شوند. برای حفظ داده‌ها:
- از Volume یا Persistent Storage استفاده کنید
- یا داده‌ها را به database انتقال دهید

## مرحله 6: مانیتورینگ

### 6.1 Logs
```bash
# در Zeabur dashboard
tail -f logs
```

### 6.2 Health Check
ربات هر 30 ثانیه status می‌فرستد

## مرحله 7: Scale کردن

### 7.1 Resource Limits
- CPU: 0.5 core
- Memory: 512MB
- کافی برای 1000+ کاربر

### 7.2 Auto-scaling
Zeabur خودکار scale می‌کند

## مرحله 8: Domain و SSL

### 8.1 Custom Domain
1. Settings → Domains
2. Add your domain
3. SSL خودکار تنظیم می‌شود

## نکات مهم:

### ✅ موارد مثبت:
- ربات کاملاً آماده deploy است
- سیستم جنگ منطقه‌ای پیاده‌سازی شده
- 6 حزب با 6 منطقه هر کدام
- سیستم خرید، جنگ و پاداش

### ⚠️ نکات مهم:
- ADMIN_ID را حتماً عوض کنید
- BOT_TOKEN را secure نگه دارید
- برای production از database استفاده کنید
- Regular backup از data files بگیرید

### 🔧 اگر مشکل داشتید:
1. Zeabur logs را چک کنید
2. Environment variables را بررسی کنید
3. Dependencies را چک کنید
4. Network connectivity تست کنید

## مرحله 9: نگهداری

### 9.1 Updates
برای آپدیت ربات:
1. کد را عوض کنید
2. Git push کنید
3. Zeabur خودکار deploy می‌کند

### 9.2 Monitoring
- Response time
- Error rates
- User activity

---

**تبریک! ربات شما آماده است 🎉**

برای سوالات بیشتر، documentation Zeabur را بخوانید یا از support آن‌ها کمک بگیرید.