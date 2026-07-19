import os
import json
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading 

# غیرفعال کردن پیام خوش‌آمدگویی پیش‌فرض pygame در ترمینال
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# --- پیکربندی و ثوابت سیستم ---
class Config:
    DATA_FILE = "juz30.json"
    PROGRESS_FILE = "user_progress.json"
    API_URL = "http://api.alquran.cloud/v1/juz/30/quran-simple"
    AUDIO_CACHE_DIR = os.path.join("audio_cache", "husary")
    LEITNER_INTERVALS = {1: 86400, 2: 172800, 3: 345600, 4: 691200, 5: 1382400}


# --- بخش چندزبانگی (Localization) ---
class LocalizationManager:
    TRANSLATIONS = {
        "fa": {
            "title": "سامانه جامع آموزش، حفظ و لایتر جزء ۳۰ قرآن کریم",
            "surah": "سوره:",
            "game_mode": "حالت بازی:",
            "start": "شروع",
            "next_page": "صفحه بعد ◀",
            "prev_page": "▶ صفحه قبل",
            "page_info": "صفحه {} از {}",
            "lang_label": "زبان / Language:",
            "audio_drag": "🔊 بشنوید و بکشید",
            "score_title": "📜 کارنامه آزمون جامع سوره {} 📜",
            "total_questions": "تعداد کل سوالات (آیات سوره): {}",
            "correct_answers": "پاسخ‌های کاملاً صحیح و بدون خطا: {}",
            "wrong_answers": "پاسخ‌های با خطا یا اصلاح‌شده: {}",
            "your_score": "نمره شما: {:.2f} از ۲۰",
            "restart_exam": "شروع مجدد آزمون جامع",
            "leitner_title": "✨ جعبه لایتر قرآنی (مرور آیات سررسید شده) ✨",
            "leitner_empty": "🌟 تبریک! امروز هیچ آیه‌ای در جعبه لایتر برای مرور وجود ندارد. 🌟",
            "bookmark_title": "✨ تمرین اختصاصی آیات نشان‌دار (ستاره‌دار) ✨",
            "bookmark_empty": "☆ هنوز هیچ آیه‌ای را نشان‌گذاری نکرده‌اید! ☆\nحین تمرین با کلیک روی ستاره خالی، آیات سخت را اضافه کنید.",
            "history_title": "📈 تاریخچه کارنامه‌ها و ارزیابی نهایی پیشرفت شما 📈",
            "history_empty": "هنوز آزمونی ثبت نشده است. ابتدا یک آزمون جامع را به پایان برسانید.",
            "table_surah": "نام سوره",
            "table_date": "تاریخ آزمون",
            "table_score": "نمره از ۲۰",
            "err_fetch": "خطا در دریافت اطلاعات: {}",
            "success_all": "بارک الله! شما سوره را تا انتها با موفقیت مرتب کردید.",
            "success_page": "آفرین! این صفحه کامل شد. با دکمه بالا به صفحه بعد بروید.",
            "success_neighbors": "بارک الله! آیات قبل و بعد را به درستی تشخیص دادید.",
            "success_fill": "عالی بود! بخش جاافتاده آیه را به درستی پیدا کردید.",
            "exam_mode_title": "آزمون جامع سوره",
            "exam_next_q": "سوال بعدی ◀",
            "neighbors_quiz_title": "آزمون همسایگی آیه",
            "completion_quiz_title": "آزمون جای خالی آیه",
            "exam_q_counter": "سوال {} از {}",
            "empty_slot": "[ جای خالی ]",
            "audio_hint": "🔊 شنیدن کل آیه جهت راهنمایی",
            "reverse_audio_suffix": " (شنیداری معکوس)",
            "modes": [
                "۱. صفحه آرایی سوره", 
                "۲. حدس قبل و بعد آیه", 
                "۳. تکمیل جای خالی آیه", 
                "۴. آزمون جامع سوره (نمره‌دهی)",
                "۵. آزمون معکوس (شنیداری)",
                "۶. جعبه لایتر (مرور روزانه)",
                "۷. آیات سخت نشان‌دار (⭐)",
                "۸. کارنامه و تاریخچه پیشرفت"
            ],
            "grades": {
                "excellent": "رتبه: ممتاز (عالی) 🌟",
                "very_good": "رتبه: بسیار خوب (جید جداً) 🏅",
                "good": "رتبه: خوب (جید) 👍",
                "needs_practice": "رتبه: نیاز به تکرار و مرور بیشتر 📖"
            }
        },
        "en": {
            "title": "Comprehensive Quran Juz 30 Memorization & Leitner System",
            "surah": "Surah:",
            "game_mode": "Game Mode:",
            "start": "Start",
            "next_page": "Next Page ◀",
            "prev_page": "▶ Prev Page",
            "page_info": "Page {} of {}",
            "lang_label": "Language:",
            "audio_drag": "🔊 Listen & Drag",
            "score_title": "📜 Exam Results for Surah {} 📜",
            "total_questions": "Total Questions (Verses): {}",
            "correct_answers": "Correct on First Attempt: {}",
            "wrong_answers": "Correct with Assistance/Errors: {}",
            "your_score": "Your Score: {:.2f} out of 20",
            "restart_exam": "Restart Comprehensive Exam",
            "leitner_title": "✨ Quranic Leitner Box (Due Reviews) ✨",
            "leitner_empty": "🌟 Congratulations! No verses are due for review today. 🌟",
            "bookmark_title": "✨ Bookmarked/Difficult Verses Quiz (⭐) ✨",
            "bookmark_empty": "☆ No bookmarked verses yet! ☆\nClick the star icon during practice to add difficult verses.",
            "history_title": "📈 Exam History & Progress Tracking 📈",
            "history_empty": "No exam history found. Complete a comprehensive exam first.",
            "table_surah": "Surah Name",
            "table_date": "Exam Date",
            "table_score": "Score / 20",
            "err_fetch": "Error fetching data: {}",
            "success_all": "Excellent! You sorted the surah successfully to the end.",
            "success_page": "Well done! This page is complete. Move to the next page.",
            "success_neighbors": "Great job! You correctly identified the surrounding verses.",
            "success_fill": "Excellent! You correctly identified the missing part of the verse.",
            "exam_mode_title": "Comprehensive Exam",
            "exam_next_q": "Next Question ◀",
            "neighbors_quiz_title": "Surrounding Verses Quiz",
            "completion_quiz_title": "Fill in the Blank Quiz",
            "exam_q_counter": "Q {} of {}",
            "empty_slot": "[ Empty Slot ]",
            "audio_hint": "🔊 Listen to the full verse for help",
            "reverse_audio_suffix": " (Reverse Audio)",
            "modes": [
                "1. Surah Page Layout", 
                "2. Guess Surrounding Verses", 
                "3. Fill in the Blank", 
                "4. Comprehensive Surah Exam",
                "5. Reverse Exam (Audio Only)",
                "6. Leitner Box (Daily Review)",
                "7. Hard/Bookmarked Verses (⭐)",
                "8. Report Card & History"
            ],
            "grades": {
                "excellent": "Grade: Excellent (Mumtaz) 🌟",
                "very_good": "Grade: Very Good (Jayyid Jiddan) 🏅",
                "good": "Grade: Good (Jayyid) 👍",
                "needs_practice": "Grade: Needs More Practice 📖"
            }
        },
        "ar": {
            "title": "النظام الشامل لتحفيظ وتكرار الجزء الثلاثون من القرآن الكريم (صندوق لايتنر)",
            "surah": "السورة:",
            "game_mode": "وضع اللعب:",
            "start": "ابدأ",
            "next_page": "الصفحة التالية ◀",
            "prev_page": "▶ الصفحة السابقة",
            "page_info": "الصفحة {} من {}",
            "lang_label": "اللغة / Language:",
            "audio_drag": "🔊 استمع واسحب",
            "score_title": "📜 نتائج الاختبار الشامل لسورة {} 📜",
            "total_questions": "إجمالي الأسئلة (آيات السورة): {}",
            "correct_answers": "الإجابات الصحيحة تماماً دون أخطاء: {}",
            "wrong_answers": "الإجابات الخاطئة أو المعدلة: {}",
            "your_score": "درجتك: {:.2f} من 20",
            "restart_exam": "إعادة الاختبار الشامل",
            "leitner_title": "✨ صندوق لايتنر القرآني (مراجعة الآيات المستحقة) ✨",
            "leitner_empty": "🌟 تهانينا! لا توجد آيات للمراجعة اليوم في صندوق لايتنر. 🌟",
            "bookmark_title": "✨ اختبار مخصص للآيات المميزة بنجمة (⭐) ✨",
            "bookmark_empty": "☆ لم تقم بتمييز أي آية بعد! ☆\nانقر على النجمة الفارغة أثناء التدريب لإضافة الآيات الصعبة هنا.",
            "history_title": "📈 سجل الاختبارات ومتابعة التقدم 📈",
            "history_empty": "لا يوجد سجل اختبارات حتى الآن. أكمل اختباراً شاملاً أولاً.",
            "table_surah": "اسم السورة",
            "table_date": "تاريخ الاختبار",
            "table_score": "الدرجة من 20",
            "err_fetch": "خطأ في جلب البيانات: {}",
            "success_all": "بارك الله فيك! لقد رتبت السورة بنجاح حتى النهاية.",
            "success_page": "أحسنتم! اكتملت هذه الصفحة. انتقل إلى الصفحة التالية.",
            "success_neighbors": "بارك الله فيك! لقد حددت الآيات السابقة والتالية بشكل صحيح.",
            "success_fill": "ممتاز! لقد وجدت الجزء الناقص من الآية بشكل صحيح.",
            "exam_mode_title": "الاختبار الشامل للسورة",
            "exam_next_q": "السؤال التالي ◀",
            "neighbors_quiz_title": "اختبار الآيات المجاورة",
            "completion_quiz_title": "اختبار إكمال الفراغ",
            "exam_q_counter": "السؤال {} من {}",
            "empty_slot": "[ فراغ ]",
            "audio_hint": "🔊 استمع للآية كاملة للمساعدة",
            "reverse_audio_suffix": " (الامتحان الصوتي المعكوس)",
            "modes": [
                "١. ترتيب صفحات السورة",
                "٢. تخمين الآية السابقة والتالية",
                "٣. إكمال فراغات الآية",
                "٤. الاختبار الشامل للسورة (نمر)",
                "٥. الاختبار الصوتي المعكوس",
                "٦. صندوق لايتنر (مراجعة يومية)",
                "٧. الآيات الصعبة المميزة بنجمة (⭐)",
                "٨. سجل النتائج ومتابعة التقدم"
            ],
            "grades": {
                "excellent": "التقدير: ممتاز 🌟",
                "very_good": "التقدير: جيد جداً 🏅",
                "good": "التقدير: جيد 👍",
                "needs_practice": "التقدير: بحاجة إلى مزيد من المراجعة والتكرار 📖"
            }
        }
    }

    def __init__(self, default_lang="fa"):
        self.current_lang = default_lang

    def set_language(self, lang):
        if lang in self.TRANSLATIONS:
            self.current_lang = lang

    def get(self, key, *args):
        text = self.TRANSLATIONS[self.current_lang].get(key, key)
        if args and isinstance(text, str):
            return text.format(*args)
        return text


# --- کلاس مدیریت داده‌ها (Data Manager) ---
class DataManager:
    @staticmethod
    def load_progress():
        if os.path.exists(Config.PROGRESS_FILE):
            with open(Config.PROGRESS_FILE, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except:
                    pass
        return {"leitner": {}, "bookmarks": [], "history": []}

    @staticmethod
    def save_progress(progress):
        with open(Config.PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=4)

    @staticmethod
    def update_leitner(surah_num, verse_num, is_correct):
        progress = DataManager.load_progress()
        key = f"{surah_num}_{verse_num}"
        current_time = int(time.time())
        
        if key not in progress["leitner"]:
            progress["leitner"][key] = {"box": 1, "next_review": 0}
            
        current_box = progress["leitner"][key]["box"]
        
        if is_correct:
            new_box = min(5, current_box + 1)
        else:
            new_box = 1  # بازگشت به جعبه اول در صورت بروز خطا
            
        next_review = current_time + Config.LEITNER_INTERVALS[new_box]
        progress["leitner"][key] = {"box": new_box, "next_review": next_review}
        DataManager.save_progress(progress)

    @staticmethod
    def split_verse_into_three(text):
        words = text.split()
        n = len(words)
        if n >= 3:
            p1_end = n // 3
            p2_end = 2 * (n // 3) + (1 if n % 3 > 0 else 0)
            part1 = " ".join(words[:p1_end])
            part2 = " ".join(words[p1_end:p2_end])
            part3 = " ".join(words[p2_end:])
        elif n == 2:
            part1 = words[0]
            part2 = ""
            part3 = words[1]
        else:
            part1 = text
            part2 = ""
            part3 = ""
        return part1, part2, part3

    @staticmethod
    def load_juz30_data():
        force_update = False
        if os.path.exists(Config.DATA_FILE):
            with open(Config.DATA_FILE, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    first_key = list(data.keys())[0]
                    first_verse = data[first_key]["verses"][0]
                    if "globalNumber" not in first_verse or "surahNumber" not in first_verse:
                        force_update = True
                except:
                    force_update = True

        if os.path.exists(Config.DATA_FILE) and not force_update:
            with open(Config.DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        try:
            session = requests.Session()
            session.trust_env = False
            response = session.get(Config.API_URL, timeout=15)
            response.raise_for_status()
            api_data = response.json()
        except Exception as e:
            return None

        surahs = {}
        for ayah in api_data['data']['ayahs']:
            surah_num = str(ayah['surah']['number'])
            surah_name = ayah['surah']['name']
            if surah_num not in surahs:
                surahs[surah_num] = {
                    "name": surah_name,
                    "englishName": ayah['surah']['englishName'],
                    "verses": []
                }
            surahs[surah_num]['verses'].append({
                "surahNumber": surah_num,
                "numberInSurah": ayah['numberInSurah'],
                "globalNumber": ayah['number'],  
                "text": ayah['text']
            })

        with open(Config.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(surahs, f, ensure_ascii=False, indent=4)
        return surahs


# --- کلاس مدیریت صوتی (Audio Manager) ---
class AudioManager:
    def __init__(self):
        pygame.mixer.init()

    def play_verse_audio(self, global_num):
        local_file_path = os.path.join(Config.AUDIO_CACHE_DIR, f"{global_num}.mp3")
        if os.path.exists(local_file_path):
            self._execute_audio_play(local_file_path)
        else:
            threading.Thread(target=self._download_and_play_thread, args=(global_num, local_file_path), daemon=True).start()

    def _download_and_play_thread(self, global_num, file_path):
        if not os.path.exists(Config.AUDIO_CACHE_DIR):
            os.makedirs(Config.AUDIO_CACHE_DIR)
        
        audio_url = f"https://cdn.alquran.cloud/media/audio/ayah/ar.husary/{global_num}"
        try:
            session = requests.Session()
            session.trust_env = False  
            response = session.get(audio_url, timeout=10, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self._execute_audio_play(file_path)
        except Exception as e:
            print(f"Background audio download failed: {e}")

    def _execute_audio_play(self, path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Audio player failed to load: {e}")

    def stop(self):
        pygame.mixer.music.stop()


# --- کلاس اصلی رابط کاربری (GUI Application) ---
class QuranPageQuizApp:
    def __init__(self, root):
        self.root = root
        self.loc = LocalizationManager("fa")  # زبان پیش‌فرض: فارسی
        self.audio_manager = AudioManager()
        
        self.surahs = DataManager.load_juz30_data()
        if not self.surahs:
            messagebox.showerror("Error / خطا", "Could not load Quran data. Check internet connection.")
            self.root.destroy()
            return

        self.root.title(self.loc.get("title"))
        self.root.geometry("1000x800")
        self.root.configure(bg="#F4EFE6") 

        self.drag_data = {"x": 0, "y": 0, "item": None, "tags": None, "start_pos": (0, 0)}
        self.slots = {}  
        self.cards = {}  
        self.correct_placements = 0
        
        self.current_verses = []  
        self.page_verses = []     
        self.current_page = 0
        self.verses_per_page = 12

        self.is_exam_mode = False
        self.exam_current_idx = 0
        self.exam_correct_count = 0
        self.exam_question_has_error = False

        self.create_widgets()
        self.update_ui_texts()

    def create_widgets(self):
        self.top_frame = tk.Frame(self.root, bg="#2C5E43", pady=10) 
        self.top_frame.pack(fill=tk.X)

        # انتخاب زبان (اضافه شدن عربی)
        self.lang_label = tk.Label(self.top_frame, text="", font=("Tahoma", 9, "bold"), fg="white", bg="#2C5E43")
        self.lang_label.pack(side=tk.RIGHT, padx=3)
        
        self.lang_combobox = ttk.Combobox(self.top_frame, values=["Persian / فارسی", "English", "Arabic / العربية"], state="readonly", width=16)
        self.lang_combobox.pack(side=tk.RIGHT, padx=3)
        self.lang_combobox.current(0)
        self.lang_combobox.bind("<<ComboboxSelected>>", self.on_language_change)

        # برچسب سوره
        self.surah_label = tk.Label(self.top_frame, text="", font=("Tahoma", 9, "bold"), fg="white", bg="#2C5E43")
        self.surah_label.pack(side=tk.RIGHT, padx=3)
        
        self.surah_options = [f"{info['name']} ({info['englishName']})" for num, info in self.surahs.items()]
        self.surah_combobox = ttk.Combobox(self.top_frame, values=self.surah_options, state="readonly", width=14, justify="right")
        self.surah_combobox.pack(side=tk.RIGHT, padx=3)
        self.surah_combobox.current(0)

        # برچسب حالت بازی
        self.mode_label = tk.Label(self.top_frame, text="", font=("Tahoma", 9, "bold"), fg="white", bg="#2C5E43")
        self.mode_label.pack(side=tk.RIGHT, padx=3)
        
        self.mode_combobox = ttk.Combobox(self.top_frame, state="readonly", width=24, justify="right")
        self.mode_combobox.pack(side=tk.RIGHT, padx=3)

        self.start_btn = tk.Button(self.top_frame, text="", command=self.on_start_click, font=("Tahoma", 9, "bold"), fg="#2C5E43", bg="#D4AF37", bd=0, padx=12, pady=3)
        self.start_btn.pack(side=tk.RIGHT, padx=8)

        self.next_btn = tk.Button(self.top_frame, text="", command=self.next_page, font=("Tahoma", 9, "bold"), fg="white", bg="#1b5e20", bd=0, padx=8, pady=3, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=10)

        self.page_label = tk.Label(self.top_frame, text="", font=("Tahoma", 10, "bold"), fg="#F4EFE6", bg="#2C5E43")
        self.page_label.pack(side=tk.LEFT, padx=10)

        self.prev_btn = tk.Button(self.top_frame, text="", command=self.prev_page, font=("Tahoma", 9, "bold"), fg="white", bg="#1b5e20", bd=0, padx=8, pady=3, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=10)

        self.canvas = tk.Canvas(self.root, bg="#FDFBF7", highlightbackground="#C5A880", highlightthickness=3)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas.tag_bind("draggable", "<Button-1>", self.on_drag_start)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag_motion)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_drag_release)
        
        self.canvas.tag_bind("slot_audio_btn", "<Button-1>", self.on_slot_audio_click)
        self.canvas.tag_bind("anchor_audio_btn", "<Button-1>", self.on_anchor_audio_click)
        self.canvas.tag_bind("star_btn", "<Button-1>", self.on_star_click)

    def on_language_change(self, event):
        selected = self.lang_combobox.current()
        if selected == 0:
            lang_code = "fa"
        elif selected == 1:
            lang_code = "en"
        else:
            lang_code = "ar"
        self.loc.set_language(lang_code)
        self.root.title(self.loc.get("title"))
        self.update_ui_texts()
        
    def update_ui_texts(self):
        self.lang_label.config(text=self.loc.get("lang_label"))
        self.surah_label.config(text=self.loc.get("surah"))
        self.mode_label.config(text=self.loc.get("game_mode"))
        self.start_btn.config(text=self.loc.get("start"))
        self.next_btn.config(text=self.loc.get("next_page"))
        self.prev_btn.config(text=self.loc.get("prev_page"))
        
        current_mode_idx = max(0, self.mode_combobox.current())
        self.mode_combobox.config(values=self.loc.get("modes"))
        self.mode_combobox.current(current_mode_idx)

    def on_start_click(self):
        selected_mode = self.mode_combobox.current()
        selected_index = self.surah_combobox.current()
        surah_keys = list(self.surahs.keys())
        selected_key = surah_keys[selected_index]
        self.current_verses = self.surahs[selected_key]['verses']
        self.is_exam_mode = False

        if selected_mode == 0:
            self.load_page_data()
        elif selected_mode == 1:
            self.start_neighbors_quiz()
        elif selected_mode == 2:
            self.start_completion_quiz()
        elif selected_mode == 3:
            self.is_exam_mode = True
            self.start_comprehensive_exam()
        elif selected_mode == 4:
            self.load_page_data(reverse_audio=True)
        elif selected_mode == 5:
            self.start_leitner_quiz()
        elif selected_mode == 6:
            self.start_bookmarked_quiz()
        elif selected_mode == 7:
            self.show_exam_history()

    # ------------------ بازی حالت اول و پنجم: صفحه آرایی / صوتی معکوس ------------------
    def load_page_data(self, reverse_audio=False):
        self.audio_manager.stop()
        self.canvas.delete("all")
        self.slots.clear()
        self.cards.clear()
        self.correct_placements = 0

        start_idx = self.current_page * self.verses_per_page
        end_idx = start_idx + self.verses_per_page
        self.page_verses = self.current_verses[start_idx:end_idx]

        total_pages = (len(self.current_verses) - 1) // self.verses_per_page + 1
        self.page_label.config(text=self.loc.get("page_info", self.current_page + 1, total_pages))
        
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if (self.current_page + 1) < total_pages else tk.DISABLED)

        self.canvas.create_rectangle(10, 10, 950, 620, outline="#C5A880", width=2)
        self.canvas.create_rectangle(15, 15, 945, 615, outline="#2C5E43", width=1)

        selected_index = self.surah_combobox.current()
        selected_key = list(self.surahs.keys())[selected_index]
        surah_title = self.surahs[selected_key]['name']
        title_text = f"✨ {surah_title}{self.loc.get('reverse_audio_suffix')} ✨" if reverse_audio else f"✨ {surah_title} ✨"
        self.canvas.create_text(480, 40, text=title_text, font=("Times", 18, "bold"), fill="#2C5E43")

        progress_data = DataManager.load_progress()

        for i, verse in enumerate(self.page_verses):
            cols = 3
            row = i // cols
            col = i % cols 
            
            x1 = 920 - (col * (240 + 25)) - 240
            y1 = 75 + (row * (60 + 15))
            x2 = x1 + 240
            y2 = y1 + 60

            slot_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="#C5A880", dash=(4, 2), width=1.5, fill="#F4EFE6")
            
            v_key = f"{verse['surahNumber']}_{verse['numberInSurah']}"
            star_char = "⭐" if v_key in progress_data["bookmarks"] else "☆"
            star_id = self.canvas.create_text(x1 + 45, y1 + 30, text=star_char, font=("Arial", 14), fill="#D4AF37", tags=("star_btn", f"star_{v_key}"))

            text_id = self.canvas.create_text(x1 + 240 - 15, y1 + 30, text=f"({verse['numberInSurah']})", font=("Tahoma", 10, "bold"), fill="#2C5E43", anchor="e")
            audio_btn = self.canvas.create_text(x1 + 20, y1 + 30, text="🔊", font=("Arial", 12), fill="#C5A880", tags=("slot_audio_btn", f"slot_id_{verse['numberInSurah']}"))

            self.slots[verse['numberInSurah']] = {
                "coords": (x1, y1, x2, y2),
                "rect_id": slot_id,
                "verse_data": verse,
                "filled": False
            }

        shuffled_verses = self.page_verses.copy()
        random.shuffle(shuffled_verses)

        pool_y = 425
        card_w, card_h = 210, 50
        pool_cols = 4
        pool_start_x = 920

        for i, verse in enumerate(shuffled_verses):
            row = i // pool_cols
            col = i % pool_cols
            
            x1 = pool_start_x - (col * (card_w + 15)) - card_w
            y1 = pool_y + (row * (card_h + 10))
            x2 = x1 + card_w
            y2 = y1 + card_h

            tag_name = f"card_{verse['numberInSurah']}"

            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#EFEBE4", outline="#8D6E63", width=1, tags=("draggable", tag_name))
            audio_btn = self.canvas.create_text(x1 + 18, y1 + card_h/2, text="🔊", font=("Arial", 12), fill="#2C5E43", tags=("draggable", tag_name, "audio_btn"))
            
            card_text = self.loc.get("audio_drag") if reverse_audio else verse['text']
            text = self.canvas.create_text(x1 + card_w - 10, y1 + card_h/2, text=card_text, font=("Arial", 11), fill="#3E2723", anchor="e", justify="right", width=card_w-45, tags=("draggable", tag_name))

            self.cards[tag_name] = {
                "original_pos": (x1, y1),
                "verse_data": verse,
                "locked": False
            }

    # ------------------ بازی حالت دوم: حدس همسایگی آیات ------------------
    def start_neighbors_quiz(self, specific_index=None, custom_verses=None):
        self.audio_manager.stop()
        self.canvas.delete("all")
        self.slots.clear()
        self.cards.clear()
        self.correct_placements = 0

        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        
        if not self.is_exam_mode:
            self.page_label.config(text=self.loc.get("neighbors_quiz_title"))

        self.canvas.create_rectangle(10, 10, 950, 620, outline="#C5A880", width=2)
        self.canvas.create_rectangle(15, 15, 945, 615, outline="#2C5E43", width=1)

        verses_source = custom_verses if custom_verses else self.current_verses
        total_verses = len(verses_source)
        if total_verses < 1:
            return
        
        anchor_idx = specific_index if specific_index is not None else random.randint(0, total_verses - 1)
        anchor_verse = verses_source[anchor_idx]

        selected_index = self.surah_combobox.current()
        selected_key = list(self.surahs.keys())[selected_index]
        surah_title = self.surahs[selected_key]['name']
        self.canvas.create_text(480, 35, text=f"✨ {surah_title} ({self.loc.get('neighbors_quiz_title')}) ✨", font=("Times", 16, "bold"), fill="#2C5E43")

        if self.is_exam_mode:
            self.canvas.create_text(120, 40, text=self.loc.get("exam_q_counter", self.exam_current_idx + 1, len(self.current_verses)), font=("Tahoma", 10, "bold"), fill="#8D6E63")

        neighbor_indices = []
        if anchor_idx - 2 >= 0: neighbor_indices.append(anchor_idx - 2)
        if anchor_idx - 1 >= 0: neighbor_indices.append(anchor_idx - 1)
        neighbor_indices.append(anchor_idx)  
        if anchor_idx + 1 < total_verses: neighbor_indices.append(anchor_idx + 1)
        if anchor_idx + 2 < total_verses: neighbor_indices.append(anchor_idx + 2)

        slot_w, slot_h = 360, 52
        start_x = 480 - slot_w / 2
        start_y = 70
        gap_y = 12

        target_verses_to_guess = []  
        progress_data = DataManager.load_progress()

        for i, idx in enumerate(neighbor_indices):
            y1 = start_y + i * (slot_h + gap_y)
            x1 = start_x
            x2 = x1 + slot_w
            y2 = y1 + slot_h

            verse = verses_source[idx]

            if idx == anchor_idx:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#C8E6C9", outline="#2E7D32", width=2)
                self.canvas.create_text(x1 + slot_w - 15, y1 + slot_h/2, text=f"({verse['numberInSurah']})", font=("Tahoma", 10, "bold"), fill="#2E7D32", anchor="e")
                self.canvas.create_text(x1 + 20, y1 + slot_h/2, text="🔊", font=("Arial", 12), fill="#2E7D32", tags=("anchor_audio_btn", f"anchor_audio_{verse['numberInSurah']}"))
                self.canvas.create_text(x1 + slot_w - 45, y1 + slot_h/2, text=verse['text'], font=("Arial", 11, "bold"), fill="#1b5e20", anchor="e", justify="right", width=slot_w-75)
                self.anchor_global_number = verse['globalNumber']
            else:
                slot_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="#C5A880", dash=(4, 2), width=1.5, fill="#F4EFE6")
                
                v_key = f"{verse['surahNumber']}_{verse['numberInSurah']}"
                star_char = "⭐" if v_key in progress_data["bookmarks"] else "☆"
                self.canvas.create_text(x1 + 45, y1 + slot_h/2, text=star_char, font=("Arial", 14), fill="#D4AF37", tags=("star_btn", f"star_{v_key}"))

                self.canvas.create_text(x1 + slot_w - 15, y1 + slot_h/2, text=f"({verse['numberInSurah']})", font=("Tahoma", 10, "bold"), fill="#2C5E43", anchor="e")
                self.canvas.create_text(x1 + 20, y1 + slot_h/2, text="🔊", font=("Arial", 12), fill="#C5A880", tags=("slot_audio_btn", f"slot_id_{verse['numberInSurah']}"))
                
                self.slots[verse['numberInSurah']] = {
                    "coords": (x1, y1, x2, y2),
                    "rect_id": slot_id,
                    "verse_data": verse,
                    "filled": False
                }
                target_verses_to_guess.append(verse)

        pool_verses = target_verses_to_guess.copy()
        all_indices = set(range(total_verses))
        used_indices = set(neighbor_indices)
        remaining_indices = list(all_indices - used_indices)
        
        distractors_count = min(2, len(remaining_indices))
        if distractors_count > 0:
            distractor_samples = random.sample(remaining_indices, distractors_count)
            for d_idx in distractor_samples:
                pool_verses.append(verses_source[d_idx])

        random.shuffle(pool_verses)

        pool_y = 445
        card_w, card_h = 210, 50
        pool_cols = 4
        pool_start_x = 920

        for i, verse in enumerate(pool_verses):
            row = i // pool_cols
            col = i % pool_cols
            
            x1 = pool_start_x - (col * (card_w + 15)) - card_w
            y1 = pool_y + (row * (card_h + 10))
            x2 = x1 + card_w
            y2 = y1 + card_h

            tag_name = f"card_{verse['numberInSurah']}"

            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#EFEBE4", outline="#8D6E63", width=1, tags=("draggable", tag_name))
            audio_btn = self.canvas.create_text(x1 + 18, y1 + card_h/2, text="🔊", font=("Arial", 12), fill="#2C5E43", tags=("draggable", tag_name, "audio_btn"))
            text = self.canvas.create_text(x1 + card_w - 10, y1 + card_h/2, text=verse['text'], font=("Arial", 11), fill="#3E2723", anchor="e", justify="right", width=card_w-45, tags=("draggable", tag_name))

            self.cards[tag_name] = {
                "original_pos": (x1, y1),
                "verse_data": verse,
                "locked": False
            }

    # ------------------ بازی حالت سوم: تکمیل جای خالی آیه ------------------
    def start_completion_quiz(self, specific_index=None, custom_verses=None):
        self.audio_manager.stop()
        self.canvas.delete("all")
        self.slots.clear()
        self.cards.clear()
        self.correct_placements = 0

        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        
        if not self.is_exam_mode:
            self.page_label.config(text=self.loc.get("completion_quiz_title"))

        self.canvas.create_rectangle(10, 10, 950, 620, outline="#C5A880", width=2)
        self.canvas.create_rectangle(15, 15, 945, 615, outline="#2C5E43", width=1)

        verses_source = custom_verses if custom_verses else self.current_verses
        total_verses = len(verses_source)
        if total_verses < 1:
            return

        if specific_index is not None:
            selected_verse = verses_source[specific_index]
        else:
            valid_verses = [v for v in verses_source if len(v['text'].split()) >= 3]
            if not valid_verses:
                valid_verses = verses_source
            selected_verse = random.choice(valid_verses)
        
        selected_index = self.surah_combobox.current()
        selected_key = list(self.surahs.keys())[selected_index]
        surah_title = self.surahs[selected_key]['name']
        self.canvas.create_text(480, 35, text=f"✨ {surah_title} ({self.loc.get('completion_quiz_title')}) ✨", font=("Times", 16, "bold"), fill="#2C5E43")

        if self.is_exam_mode:
            self.canvas.create_text(120, 40, text=self.loc.get("exam_q_counter", self.exam_current_idx + 1, total_verses), font=("Tahoma", 10, "bold"), fill="#8D6E63")

        self.canvas.create_text(480, 85, text=f"{self.loc.get('surah')} {selected_verse['numberInSurah']}", font=("Tahoma", 12, "bold"), fill="#8D6E63")
        self.canvas.create_text(480, 125, text=self.loc.get("audio_hint"), font=("Tahoma", 10, "bold"), fill="#2C5E43", tags=("anchor_audio_btn", f"anchor_audio_{selected_verse['numberInSurah']}"))
        self.anchor_global_number = selected_verse['globalNumber']

        parts = DataManager.split_verse_into_three(selected_verse['text'])
        hidden_idx = random.randint(0, 2)  

        block_w, block_h = 240, 60
        gap_x = 25
        total_w = 3 * block_w + 2 * gap_x
        start_x = 480 - total_w / 2
        y1 = 180
        y2 = y1 + block_h

        correct_missing_text = parts[hidden_idx]
        progress_data = DataManager.load_progress()

        for i in range(3):
            col_idx = 2 - i  
            x1 = start_x + col_idx * (block_w + gap_x)
            x2 = x1 + block_w

            part_text = parts[i]

            if i == hidden_idx:
                slot_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="#C5A880", dash=(4, 2), width=2, fill="#FDFBF7")
                self.canvas.create_text(x1 + block_w/2, y1 + block_h/2, text=self.loc.get("empty_slot"), font=("Tahoma", 10, "italic"), fill="#C5A880")
                
                v_key = f"{selected_verse['surahNumber']}_{selected_verse['numberInSurah']}"
                star_char = "⭐" if v_key in progress_data["bookmarks"] else "☆"
                self.canvas.create_text(x1 + 25, y1 + block_h/2, text=star_char, font=("Arial", 14), fill="#D4AF37", tags=("star_btn", f"star_{v_key}"))

                self.slots[selected_verse['numberInSurah']] = {
                    "coords": (x1, y1, x2, y2),
                    "rect_id": slot_id,
                    "verse_data": {"numberInSurah": selected_verse['numberInSurah'], "text": correct_missing_text, "surahNumber": selected_verse['surahNumber']},
                    "filled": False
                }
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#F4EFE6", outline="#C5A880", width=1)
                self.canvas.create_text(x1 + block_w/2, y1 + block_h/2, text=part_text, font=("Arial", 12), fill="#3E2723", width=block_w-15, justify="center")

        pool_items = [{"text": correct_missing_text, "correct": True, "num": selected_verse['numberInSurah']}]

        other_verses = [v for v in verses_source if v['numberInSurah'] != selected_verse['numberInSurah']]
        distractor_count = min(3, len(other_verses))
        
        if distractor_count > 0:
            sampled_distractors = random.sample(other_verses, distractor_count)
            for dv in sampled_distractors:
                dp1, dp2, dp3 = DataManager.split_verse_into_three(dv['text'])
                d_part = random.choice([p for p in [dp1, dp2, dp3] if p != ""]) 
                pool_items.append({"text": d_part, "correct": False, "num": dv['numberInSurah']})

        random.shuffle(pool_items)

        pool_y = 445
        card_w, card_h = 210, 50
        pool_cols = 4
        pool_start_x = 920

        for i, item in enumerate(pool_items):
            row = i // pool_cols
            col = i % pool_cols
            
            x1 = pool_start_x - (col * (card_w + 15)) - card_w
            y1 = pool_y + (row * (card_h + 10))
            x2 = x1 + card_w
            y2 = y1 + card_h

            tag_name = f"card_{item['num']}"

            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#EFEBE4", outline="#8D6E63", width=1, tags=("draggable", tag_name))
            text = self.canvas.create_text(x1 + card_w/2, y1 + card_h/2, text=item['text'], font=("Arial", 11), fill="#3E2723", width=card_w-20, justify="center", tags=("draggable", tag_name))

            self.cards[tag_name] = {
                "original_pos": (x1, y1),
                "verse_data": {"numberInSurah": item['num'], "text": item['text'], "surahNumber": selected_verse['surahNumber']},
                "locked": False
            }

    # ------------------ بازی حالت چهارم: آزمون جامع سوره ------------------
    def start_comprehensive_exam(self):
        self.audio_manager.stop()
        self.exam_current_idx = 0
        self.exam_correct_count = 0
        self.exam_question_has_error = False
        
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.page_label.config(text=self.loc.get("exam_mode_title"))

        self.load_exam_question()

    def load_exam_question(self):
        self.exam_question_has_error = False
        question_type = random.choice([1, 2]) 
        if question_type == 1:
            self.start_completion_quiz(specific_index=self.exam_current_idx)
        else:
            self.start_neighbors_quiz(specific_index=self.exam_current_idx)

    def on_exam_next_click(self):
        if not self.exam_question_has_error:
            self.exam_correct_count += 1
            
        self.exam_current_idx += 1
        
        if self.exam_current_idx < len(self.current_verses):
            self.load_exam_question()
        else:
            self.show_exam_results()

    def show_exam_results(self):
        self.audio_manager.stop()
        self.canvas.delete("all")
        self.slots.clear()
        self.cards.clear()

        total_q = len(self.current_verses)
        score_20 = (self.exam_correct_count / total_q) * 20
        wrong_count = total_q - self.exam_correct_count

        grades = self.loc.get("grades")
        if score_20 >= 19:
            grade_str = grades["excellent"]
            grade_color = "#2E7D32"
        elif score_20 >= 17:
            grade_str = grades["very_good"]
            grade_color = "#1565C0"
        elif score_20 >= 15:
            grade_str = grades["good"]
            grade_color = "#E65100"
        else:
            grade_str = grades["needs_practice"]
            grade_color = "#C62828"

        selected_index = self.surah_combobox.current()
        selected_key = list(self.surahs.keys())[selected_index]
        surah_title = self.surahs[selected_key]['name']

        # ثبت تاریخچه آزمون در فایل پیشرفت
        progress = DataManager.load_progress()
        date_str = time.strftime("%Y-%m-%d %H:%M")
        progress["history"].append({
            "surah": surah_title,
            "score": round(score_20, 2),
            "date": date_str
        })
        DataManager.save_progress(progress)

        self.canvas.create_rectangle(150, 60, 810, 560, outline="#C5A880", width=3, fill="#FDFBF7")
        self.canvas.create_rectangle(158, 68, 802, 552, outline="#2C5E43", width=1.5)

        self.canvas.create_text(480, 120, text=self.loc.get("score_title", surah_title), font=("Tahoma", 15, "bold"), fill="#2C5E43")
        self.canvas.create_text(480, 200, text=self.loc.get("total_questions", total_q), font=("Tahoma", 11, "bold"), fill="#3E2723")
        self.canvas.create_text(480, 240, text=self.loc.get("correct_answers", self.exam_correct_count), font=("Tahoma", 11, "bold"), fill="#2E7D32")
        self.canvas.create_text(480, 280, text=self.loc.get("wrong_answers", wrong_count), font=("Tahoma", 11, "bold"), fill="#C62828")
        
        self.canvas.create_rectangle(350, 330, 610, 420, fill="#EFEBE4", outline="#C5A880", width=1.5)
        self.canvas.create_text(480, 375, text=self.loc.get("your_score", score_20), font=("Tahoma", 14, "bold"), fill="#2C5E43")
        self.canvas.create_text(480, 460, text=grade_str, font=("Tahoma", 13, "bold"), fill=grade_color)

        restart_btn = tk.Button(self.root, text=self.loc.get("restart_exam"), command=self.start_comprehensive_exam, font=("Tahoma", 10, "bold"), fg="white", bg="#D4AF37", activebackground="#C5A880", bd=0, padx=20, pady=8)
        self.canvas.create_window(480, 515, window=restart_btn)

    # ------------------ بازی حالت ششم: جعبه لایتر (مرور روزانه) ------------------
    def start_leitner_quiz(self):
        self.audio_manager.stop()
        self.canvas.delete("all")
        self.slots.clear()
        self.cards.clear()
        self.correct_placements = 0

        self.canvas.create_rectangle(10, 10, 950, 620, outline="#C5A880", width=2)
        self.canvas.create_rectangle(15, 15, 945, 615, outline="#2C5E43", width=1)
        self.canvas.create_text(480, 40, text=self.loc.get("leitner_title"), font=("Times", 16, "bold"), fill="#2C5E43")

        progress = DataManager.load_progress()
        current_time = int(time.time())
        due_keys = []

        for key, info in progress["leitner"].items():
            if info["next_review"] <= current_time:
                due_keys.append(key)

        if not due_keys:
            self.canvas.create_text(480, 300, text=self.loc.get("leitner_empty"), font=("Tahoma", 13, "bold"), fill="#2e7d32")
            return

        chosen_key = random.choice(due_keys)
        s_num, v_num = chosen_key.split("_")
        
        selected_verse = None
        for verse in self.surahs[s_num]["verses"]:
            if str(verse["numberInSurah"]) == v_num:
                selected_verse = verse
                break

        if selected_verse:
            self.current_verses = self.surahs[s_num]["verses"]
            self.start_completion_quiz(specific_index=int(v_num)-1)

    # ------------------ بازی حالت هفتم: آزمون آیات سخت (نشان‌دار) ------------------
    def start_bookmarked_quiz(self):
        self.audio_manager.stop()
        self.canvas.delete("all")
        self.slots.clear()
        self.cards.clear()
        self.correct_placements = 0

        self.canvas.create_rectangle(10, 10, 950, 620, outline="#C5A880", width=2)
        self.canvas.create_rectangle(15, 15, 945, 615, outline="#2C5E43", width=1)
        self.canvas.create_text(480, 40, text=self.loc.get("bookmark_title"), font=("Times", 16, "bold"), fill="#2C5E43")

        progress = DataManager.load_progress()
        if not progress["bookmarks"]:
            self.canvas.create_text(480, 300, text=self.loc.get("bookmark_empty"), font=("Tahoma", 12), fill="#c62828", justify="center")
            return

        chosen_key = random.choice(progress["bookmarks"])
        s_num, v_num = chosen_key.split("_")
        
        selected_verse = None
        for verse in self.surahs[s_num]["verses"]:
            if str(verse["numberInSurah"]) == v_num:
                selected_verse = verse
                break

        if selected_verse:
            self.current_verses = self.surahs[s_num]["verses"]
            self.start_completion_quiz(specific_index=int(v_num)-1)

    # ------------------ بازی حالت هشتم: کارنامه‌ها و نمودار پیشرفت ------------------
    def show_exam_history(self):
        self.audio_manager.stop()
        self.canvas.delete("all")
        self.slots.clear()
        self.cards.clear()

        self.canvas.create_rectangle(10, 10, 950, 620, outline="#C5A880", width=2)
        self.canvas.create_rectangle(15, 15, 945, 615, outline="#2C5E43", width=1)
        self.canvas.create_text(480, 50, text=self.loc.get("history_title"), font=("Tahoma", 14, "bold"), fill="#2C5E43")

        progress = DataManager.load_progress()
        history = progress.get("history", [])

        if not history:
            self.canvas.create_text(480, 300, text=self.loc.get("history_empty"), font=("Tahoma", 12), fill="#3e2723")
            return

        history_to_show = history[-7:]
        start_y = 130
        gap_y = 55

        self.canvas.create_rectangle(150, start_y - 30, 810, start_y, fill="#2C5E43", outline="")
        self.canvas.create_text(700, start_y - 15, text=self.loc.get("table_surah"), font=("Tahoma", 10, "bold"), fill="white")
        self.canvas.create_text(480, start_y - 15, text=self.loc.get("table_date"), font=("Tahoma", 10, "bold"), fill="white")
        self.canvas.create_text(260, start_y - 15, text=self.loc.get("table_score"), font=("Tahoma", 10, "bold"), fill="white")

        for idx, item in enumerate(history_to_show):
            y = start_y + idx * gap_y
            self.canvas.create_rectangle(150, y, 810, y + 45, fill="#EFEBE4" if idx % 2 == 0 else "#FDFBF7", outline="#C5A880", width=0.5)
            
            self.canvas.create_text(700, y + 22, text=item["surah"], font=("Tahoma", 10, "bold"), fill="#3E2723")
            self.canvas.create_text(480, y + 22, text=item["date"], font=("Tahoma", 10), fill="#3E2723")
            
            score_color = "#2E7D32" if item["score"] >= 15 else "#C62828"
            self.canvas.create_text(260, y + 22, text=f"{item['score']}", font=("Tahoma", 11, "bold"), fill=score_color)

    # ------------------ مدیریت نشان‌گذاری آیات (ستاره) ------------------
    def on_star_click(self, event):
        item = self.canvas.find_withtag("current")[0]
        tags = self.canvas.gettags(item)
        star_tag = [t for t in tags if t.startswith("star_")][0]
        v_key = star_tag.replace("star_", "") 

        progress = DataManager.load_progress()
        if v_key in progress["bookmarks"]:
            progress["bookmarks"].remove(v_key)
            self.canvas.itemconfig(item, text="☆")
        else:
            progress["bookmarks"].append(v_key)
            self.canvas.itemconfig(item, text="⭐")
        
        DataManager.save_progress(progress)

    def on_slot_audio_click(self, event):
        item = self.canvas.find_withtag("current")[0]
        tags = self.canvas.gettags(item)
        audio_tag = [t for t in tags if t.startswith("slot_id_")][0]
        verse_num = int(audio_tag.split("_")[2]) 

        global_num = None
        for slot_num, slot_info in self.slots.items():
            if slot_num == verse_num:
                global_num = slot_info["verse_data"]["globalNumber"]
                break

        if global_num:
            self.audio_manager.play_verse_audio(global_num)

    def on_anchor_audio_click(self, event):
        if hasattr(self, 'anchor_global_number'):
            self.audio_manager.play_verse_audio(self.anchor_global_number)

    def next_page(self):
        total_pages = (len(self.current_verses) - 1) // self.verses_per_page + 1
        if self.current_page + 1 < total_pages:
            self.current_page += 1
            self.load_page_data()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page_data()

    # ------------------ رویدادهای اصلی Drag and Drop ------------------
    def on_drag_start(self, event):
        item = self.canvas.find_withtag("current")[0]
        tags = self.canvas.gettags(item)
        card_tag = [t for t in tags if t.startswith("card_")][0]

        if "audio_btn" in tags:
            global_num = self.cards[card_tag]["verse_data"]["globalNumber"]
            self.audio_manager.play_verse_audio(global_num)
            return 

        if self.cards[card_tag]["locked"]:
            return  

        self.drag_data["item"] = item
        self.drag_data["tags"] = card_tag
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["start_pos"] = self.cards[card_tag]["original_pos"]
        
        self.canvas.tag_raise(card_tag)

    def on_drag_motion(self, event):
        card_tag = self.drag_data["tags"]
        if not card_tag or self.cards[card_tag]["locked"]:
            return

        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        self.canvas.move(card_tag, dx, dy)
        
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_release(self, event):
        card_tag = self.drag_data["tags"]
        if not card_tag or self.cards[card_tag]["locked"]:
            return

        card_coords = self.canvas.bbox(card_tag)
        cx = (card_coords[0] + card_coords[2]) / 2
        cy = (card_coords[1] + card_coords[3]) / 2

        matched_slot_id = None
        verse_num = self.cards[card_tag]["verse_data"]["numberInSurah"]

        for slot_num, slot_info in self.slots.items():
            s_coords = slot_info["coords"]
            if s_coords[0] <= cx <= s_coords[2] and s_coords[1] <= cy <= s_coords[3]:
                if slot_num == verse_num: 
                    matched_slot_id = slot_num
                break

        if matched_slot_id:
            slot_coords = self.slots[matched_slot_id]["coords"]
            orig_coords = self.canvas.bbox(card_tag)
            dx = slot_coords[0] - orig_coords[0]
            dy = slot_coords[1] - orig_coords[1]
            self.canvas.move(card_tag, dx, dy)

            items = self.canvas.find_withtag(card_tag)
            for item in items:
                if self.canvas.type(item) == "rectangle":
                    self.canvas.itemconfig(item, fill="#C8E6C9", outline="#2E7D32") 

            self.cards[card_tag]["locked"] = True
            self.slots[matched_slot_id]["filled"] = True
            self.correct_placements += 1

            v_data = self.cards[card_tag]["verse_data"]
            DataManager.update_leitner(v_data.get("surahNumber", "0"), verse_num, is_correct=True)

            if self.correct_placements == len(self.slots):
                if self.is_exam_mode:
                    next_q_btn = tk.Button(self.root, text=self.loc.get("exam_next_q"), command=self.on_exam_next_click, font=("Tahoma", 10, "bold"), fg="white", bg="#D4AF37", activebackground="#C5A880", bd=0, padx=25, pady=6)
                    self.canvas.create_window(480, 370, window=next_q_btn, tags="next_q_btn_window")
                else:
                    selected_mode = self.mode_combobox.current()
                    if selected_mode in (0, 4):
                        total_pages = (len(self.current_verses) - 1) // self.verses_per_page + 1
                        if self.current_page + 1 == total_pages:
                            messagebox.showinfo("Success / موفقیت", self.loc.get("success_all"))
                        else:
                            messagebox.showinfo("Success / موفقیت", self.loc.get("success_page"))
                    elif selected_mode == 1:
                        messagebox.showinfo("Success / موفقیت", self.loc.get("success_neighbors"))
                    else:
                        messagebox.showinfo("Success / موفقیت", self.loc.get("success_fill"))
        else:
            v_data = self.cards[card_tag]["verse_data"]
            DataManager.update_leitner(v_data.get("surahNumber", "0"), verse_num, is_correct=False)

            if self.is_exam_mode:
                self.exam_question_has_error = True  

            orig_x, orig_y = self.drag_data["start_pos"]
            curr_coords = self.canvas.bbox(card_tag)
            dx = orig_x - curr_coords[0]
            dy = orig_y - curr_coords[1]
            self.canvas.move(card_tag, dx, dy)

        self.drag_data = {"x": 0, "y": 0, "item": None, "tags": None, "start_pos": (0, 0)}


if __name__ == "__main__":
    root = tk.Tk()
    app = QuranPageQuizApp(root)
    root.mainloop()