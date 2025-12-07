import 'package:flutter/material.dart';
// import 'package:url_launcher/url_launcher.dart'; // 나중에 실제 링크 이동 시 필요

class PlaylistResultPage extends StatelessWidget {
  // 1. 이전 화면에서 전달받을 데이터 변수 선언
  final String userName;
  final List<dynamic> playlistData; // Django가 준 리스트

  const PlaylistResultPage({
    super.key,
    required this.userName,
    required this.playlistData, // 2. 생성자 필수 인자로 추가
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, // 다크 모드 유지
      appBar: AppBar(
        backgroundColor: Colors.black,
        title: const Text(
          'Your Playlist Ready! 🎵',
          style: TextStyle(color: Colors.white),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          // 상단 안내 문구
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Text(
              '$userName님의 취향을 저격할\nGroovia 믹스가 완성되었습니다!',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white, fontSize: 18),
            ),
          ),

          // 3. 분석 결과 리스트 보여주기 (여기가 핵심!)
          Expanded(
            child: playlistData.isEmpty
                ? const Center(
                    child: Text(
                      "추천 결과가 없습니다.",
                      style: TextStyle(color: Colors.grey),
                    ),
                  )
                : ListView.builder(
                    itemCount: playlistData.length,
                    itemBuilder: (context, index) {
                      final track = playlistData[index]; // 데이터 하나 꺼내기

                      return Container(
                        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E1E1E), // 카드 배경색
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(12),
                          // 앨범 이미지
                          leading: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: (track['album_image'] != null && track['album_image'] != "")
                                ? Image.network(
                                    track['album_image'],
                                    width: 60,
                                    height: 60,
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) =>
                                        Container(width: 60, height: 60, color: Colors.grey),
                                  )
                                : Container(width: 60, height: 60, color: Colors.grey, child: const Icon(Icons.music_note)),
                          ),
                          
                          // 노래 제목
                          title: Text(
                            track['title'] ?? "Unknown Title",
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          
                          // 가수 이름
                          subtitle: Padding(
                            padding: const EdgeInsets.only(top: 4.0),
                            child: Text(
                              track['artist'] ?? "Unknown Artist",
                              style: const TextStyle(color: Colors.grey),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          
                          // 재생 아이콘 (장식용)
                          trailing: const Icon(
                            Icons.play_circle_fill,
                            color: Color(0xFF1DB954), // Spotify Green
                            size: 40,
                          ),
                          
                          onTap: () {
                            // 클릭 시 동작 (나중에 링크 이동 기능 넣으면 됨)
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text("'${track['title']}' 선택됨")),
                            );
                          },
                        ),
                      );
                    },
                  ),
          ),

          // 하단 버튼 (홈으로 가기)
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: ElevatedButton(
              onPressed: () =>
                  Navigator.popUntil(context, (route) => route.isFirst),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[800],
                padding: const EdgeInsets.symmetric(
                  horizontal: 30,
                  vertical: 15,
                ),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30)),
              ),
              child: const Text(
                "Back to Home",
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }
}