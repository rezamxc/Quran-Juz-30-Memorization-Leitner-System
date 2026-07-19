import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const QuranApp());
}

class QuranApp extends StatelessWidget {
  const QuranApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Quran Juz 30 Memorization',
      theme: ThemeData(
        primarySwatch: Colors.green,
        scaffoldBackgroundColor: const Color(0xFFF4EFE6),
      ),
      debugShowCheckedModeBanner: false,
      home: const QuranHomePage(),
    );
  }
}

class Verse {
  final String text;
  final int numberInSurah;
  final int globalNumber;
  final String surahNumber;

  Verse({
    required this.text,
    required this.numberInSurah,
    required this.globalNumber,
    required this.surahNumber,
  });

  factory Verse.fromJson(Map<String, dynamic> json, String surahNum) {
    return Verse(
      text: json['text'],
      numberInSurah: json['numberInSurah'],
      globalNumber: json['number'],
      surahNumber: surahNum,
    );
  }
}

class Surah {
  final String number;
  final String name;
  final String englishName;
  final List<Verse> verses;

  Surah({
    required this.number,
    required this.name,
    required this.englishName,
    required this.verses,
  });
}

class QuranHomePage extends StatefulWidget {
  const QuranHomePage({super.key});

  @override
  State<QuranHomePage> createState() => _QuranHomePageState();
}

class _QuranHomePageState extends State<QuranHomePage> {
  String _currentLang = 'fa';
  final AudioPlayer _audioPlayer = AudioPlayer();
  
  bool _isLoading = true;
  List<Surah> _surahs = [];
  Surah? _selectedSurah;
  
  List<Verse> _shuffledVerses = [];
  Map<int, Verse?> _slots = {}; // numberInSurah -> Placed Verse

  // ترجمه‌ها
  final Map<String, Map<String, String>> _loc = {
    'fa': {
      'title': 'سامانه حفظ جزء ۳۰ قرآن کریم',
      'surah': 'سوره:',
      'lang': 'زبان:',
      'loading': 'در حال دریافت اطلاعات قرآن...',
      'audio_hint': '🔊 برای شنیدن صوت لمس کنید',
      'success': 'بارک الله! سوره را با موفقیت مرتب کردید.',
    },
    'en': {
      'title': 'Quran Juz 30 Memorization',
      'surah': 'Surah:',
      'lang': 'Language:',
      'loading': 'Loading Quran data...',
      'audio_hint': '🔊 Tap to play audio',
      'success': 'Excellent! You sorted the Surah successfully.',
    },
    'ar': {
      'title': 'نظام تحفيظ الجزء الثلاثين',
      'surah': 'السورة:',
      'lang': 'اللغة:',
      'loading': 'جاري تحميل بيانات القرآن...',
      'audio_hint': '🔊 اضغط للاستماع للتلاوة',
      'success': 'بارك الله فيك! لقد رتبت السورة بنجاح.',
    }
  };

  @override
  void initState() {
    super.initState();
    _fetchQuranData();
  }

  Future<void> _fetchQuranData() async {
    try {
      final response = await http.get(Uri.parse('http://api.alquran.cloud/v1/juz/30/quran-simple'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        Map<String, Surah> surahMap = {};

        for (var ayah in data['data']['ayahs']) {
          String sNum = ayah['surah']['number'].toString();
          String sName = ayah['surah']['name'];
          String sEngName = ayah['surah']['englishName'];

          if (!surahMap.containsKey(sNum)) {
            surahMap[sNum] = Surah(
              number: sNum,
              name: sName,
              englishName: sEngName,
              verses: [],
            );
          }
          surahMap[sNum]!.verses.add(Verse.fromJson(ayah, sNum));
        }

        setState(() {
          _surahs = surahMap.values.toList();
          if (_surahs.isNotEmpty) {
            _selectedSurah = _surahs.first;
            _setupGame();
          }
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _setupGame() {
    if (_selectedSurah == null) return;
    _slots.clear();
    for (var v in _selectedSurah!.verses) {
      _slots[v.numberInSurah] = null;
    }
    _shuffledVerses = List.from(_selectedSurah!.verses)..shuffle();
  }

  void _playAudio(int globalNum) async {
    await _audioPlayer.stop();
    String url = "https://cdn.alquran.cloud/media/audio/ayah/ar.husary/$globalNum";
    await _audioPlayer.play(UrlSource(url));
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(color: Colors.green),
              const SizedBox(height: 15),
              Text(_loc[_currentLang]!['loading']!, style: const TextStyle(fontFamily: 'Tahoma')),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(_loc[_currentLang]!['title']!, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        backgroundColor: const Color(0xFF2C5E43),
        elevation: 2,
      ),
      body: Column(
        children: [
          // بخش تنظیمات بالا
          Container(
            color: const Color(0xFF2C5E43),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // سوره
                Row(
                  children: [
                    Text(_loc[_currentLang]!['surah']!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    const SizedBox(width: 5),
                    DropdownButton<Surah>(
                      dropdownColor: const Color(0xFF2C5E43),
                      value: _selectedSurah,
                      style: const TextStyle(color: Colors.white),
                      items: _surahs.map((s) {
                        return DropdownMenuItem<Surah>(
                          value: s,
                          child: Text("${s.name} (${s.englishName})"),
                        );
                      }).toList(),
                      onChanged: (val) {
                        setState(() {
                          _selectedSurah = val;
                          _setupGame();
                        });
                      },
                    ),
                  ],
                ),
                // زبان
                Row(
                  children: [
                    Text(_loc[_currentLang]!['lang']!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    const SizedBox(width: 5),
                    DropdownButton<String>(
                      dropdownColor: const Color(0xFF2C5E43),
                      value: _currentLang,
                      style: const TextStyle(color: Colors.white),
                      items: const [
                        DropdownMenuItem(value: 'fa', child: Text('فارسی')),
                        DropdownMenuItem(value: 'en', child: Text('English')),
                        DropdownMenuItem(value: 'ar', child: Text('العربية')),
                      ],
                      onChanged: (val) {
                        if (val != null) {
                          setState(() {
                            _currentLang = val;
                          });
                        }
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // فضای اصلی Drag and Drop
          Expanded(
            child: Row(
              children: [
                // ستون اسلات‌ها (جایگاه رها کردن آیات)
                Expanded(
                  flex: 3,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(10),
                    itemCount: _selectedSurah?.verses.length ?? 0,
                    itemBuilder: (context, index) {
                      final verse = _selectedSurah!.verses[index];
                      final placed = _slots[verse.numberInSurah];
                      
                      return DragTarget<Verse>(
                        onAcceptWithDetails: (details) {
                          if (details.data.numberInSurah == verse.numberInSurah) {
                            setState(() {
                              _slots[verse.numberInSurah] = details.data;
                              _shuffledVerses.remove(details.data);
                              
                              if (_shuffledVerses.isEmpty) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text(_loc[_currentLang]!['success']!)),
                                );
                              }
                            });
                          }
                        },
                        builder: (context, candidateData, rejectedData) {
                          return Container(
                            margin: const EdgeInsets.symmetric(vertical: 5),
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: placed != null ? const Color(0xFFC8E6C9) : Colors.white,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: placed != null ? Colors.green : const Color(0xFFC5A880),
                                width: placed != null ? 2 : 1.5,
                              ),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.volume_up, color: Colors.green),
                                  onPressed: () => _playAudio(verse.globalNumber),
                                ),
                                Expanded(
                                  child: Text(
                                    placed != null ? placed.text : "(${verse.numberInSurah}) ........................................",
                                    textAlign: TextAlign.right,
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: placed != null ? FontWeight.bold : FontWeight.normal,
                                      color: placed != null ? const Color(0xFF1B5E20) : Colors.grey,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      );
                    },
                  ),
                ),
                
                // ستون کارت‌ها (آیتم‌های قابل کشیدن)
                Expanded(
                  flex: 2,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(10),
                    itemCount: _shuffledVerses.length,
                    itemBuilder: (context, index) {
                      final verse = _shuffledVerses[index];
                      return Draggable<Verse>(
                        data: verse,
                        feedback: Material(
                          color: Colors.transparent,
                          child: Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: Colors.amber[100],
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.amber, width: 2),
                            ),
                            child: Text(verse.text, style: const TextStyle(fontSize: 14)),
                          ),
                        ),
                        childWhenDragging: Opacity(
                          opacity: 0.4,
                          child: Container(
                            margin: const EdgeInsets.symmetric(vertical: 5),
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.grey[300],
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(verse.text, textAlign: TextAlign.right),
                          ),
                        ),
                        child: Card(
                          margin: const EdgeInsets.symmetric(vertical: 5),
                          color: const Color(0xFFEFEBE4),
                          child: Padding(
                            padding: const EdgeInsets.all(12.0),
                            child: Text(
                              verse.text,
                              textAlign: TextAlign.right,
                              style: const TextStyle(fontSize: 14, color: Color(0xFF3E2723)),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}