import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_application_3/screens/playlist_result_page.dart';
import 'playlist_result_page.dart';
import 'package:http/http.dart' as http;

class SongInputPage extends StatefulWidget {
  final String userName;

  const SongInputPage({super.key, required this.userName,});

  @override
  State<SongInputPage> createState() => _SongInputPageState();
}

class _SongInputPageState extends State<SongInputPage> {
  final TextEditingController _songController = TextEditingController();
  final List<String> _songs = [];

  void _addSong() {
    String song = _songController.text.trim();
    if (song.isEmpty) return;

    setState(() {
      _songs.add(song);
      _songController.clear();
    });
  }

  void _removeSong(int index) {
    setState(() {
      _songs.removeAt(index);
    });
  }

  Future<void> _analyzeSongs() async {
    if (_songs.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('분석할 URL을 한 개 이상 입력해주세요!')));
      return;
    }
    
    // 이후 Django API 연동으로 대체 예정
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('분석을 시작합니다...')));

    // TODO: 다음 화면(로딩 → 카테고리 결과)으로 이동
    final String apiUrl = "https://ungifted-witchingly-sol.ngrok-free.dev/api/spotify/process-urls/";

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json"},

        body: jsonEncode({
          "urls": _songs,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));

        List<dynamic> resultPlaylist = data['playlist'] ?? [];

        if (resultPlaylist.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('추천 결과가 없습니다. 다른 노래를 넣어보세요!')),
          );
          return;
        }

        if (!mounted) return;

        Navigator.push(
          context,
          MaterialPageRoute(
            builder:(context) => PlaylistResultPage(
              userName: widget.userName,
              playlistData: resultPlaylist,
            ),
          ),
        );
      } else {
        print('Server Error: ${response.body}');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('분석 실패: ${response.statusCode}')),
        );
      }
    } catch (e) {
      print('Connection Error: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('서버 연결 실패: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        title: Text(
          'Hi, ${widget.userName} 👋',
          style: const TextStyle(color: Colors.white),
        ),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Enter songs or artists',
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            const SizedBox(height: 12),

            // 입력창
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _songController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'e.g. Perfect - Ed Sheeran',
                      hintStyle: const TextStyle(color: Colors.grey),
                      filled: true,
                      fillColor: const Color(0xFF1E1E1E),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        vertical: 14,
                        horizontal: 16,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _addSong,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.greenAccent[400],
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 14,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: const Text('Add'),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // 입력된 노래 리스트
            Expanded(
              child: _songs.isEmpty
                  ? const Center(
                      child: Text(
                        'No songs added yet 🎵',
                        style: TextStyle(color: Colors.grey),
                      ),
                    )
                  : ListView.builder(
                      itemCount: _songs.length,
                      itemBuilder: (context, index) {
                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E1E1E),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: ListTile(
                            title: Text(
                              _songs[index],
                              style: const TextStyle(color: Colors.white),
                            ),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () => _removeSong(index),
                            ),
                          ),
                        );
                      },
                    ),
            ),

            // 분석 버튼
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _analyzeSongs,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.greenAccent[400],
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Analyze & Get Playlist 🎧',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
