"""
Seed script: creates demo data for AcadConnect
Run: venv\Scripts\python seed.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.wellness.models import MotivationalQuote

quotes = [
    ("Believe you can and you're halfway there.", "Theodore Roosevelt", "general"),
    ("The secret of getting ahead is getting started.", "Mark Twain", "study"),
    ("It always seems impossible until it's done.", "Nelson Mandela", "general"),
    ("You don't have to see the whole staircase, just take the first step.", "Martin Luther King Jr.", "stress"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill", "general"),
    ("The only way to do great work is to love what you do.", "Steve Jobs", "achievement"),
    ("In the middle of every difficulty lies opportunity.", "Albert Einstein", "stress"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson", "study"),
    ("Education is the most powerful weapon you can use to change the world.", "Nelson Mandela", "study"),
    ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs", "wellness"),
    ("Take care of your body. It's the only place you have to live.", "Jim Rohn", "wellness"),
    ("Rest when you're weary. Refresh and renew yourself.", "Ralph Waldo Emerson", "wellness"),
    ("The greatest glory in living lies not in never falling, but in rising every time we fall.", "Nelson Mandela", "stress"),
    ("Life is what happens when you're busy making other plans.", "John Lennon", "general"),
    ("It's okay not to be okay — as long as you don't stop trying.", "Unknown", "stress"),
    ("You are braver than you believe and stronger than you seem.", "A.A. Milne", "stress"),
    ("Small steps every day lead to big change.", "Unknown", "study"),
    ("Your grades don't define you, but your effort does.", "Unknown", "achievement"),
    ("Progress, not perfection.", "Unknown", "wellness"),
    ("A year from now, you'll wish you started today.", "Karen Lamb", "study"),
]

created = 0
for text, author, category in quotes:
    _, made = MotivationalQuote.objects.get_or_create(text=text, defaults={'author': author, 'category': category})
    if made:
        created += 1

print(f"Seeded {created} new motivational quotes. Total: {MotivationalQuote.objects.count()}")
print("Done! Now run: venv\\Scripts\\python manage.py runserver")
