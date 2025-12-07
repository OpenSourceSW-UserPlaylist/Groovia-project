import 'package:flutter/material.dart';
import 'song_screen.dart';
import 'song_input_page.dart'; // SongInputPage import 추가

// 1. 더미 데이터 모델
class Album {
  final String title;
  final String imageUrl;
  final String subtitle;

  Album(this.title, this.imageUrl, this.subtitle);
}

// 2. 더미 데이터 리스트 (이전과 동일)
final List<Album> topVibes = [
  Album('Dark Academia', 'assets/images/dark_academia.png', 'Playlist'),
  Album('Chill Rap', 'assets/images/chill_rap.png', 'Playlist'),
  Album('LoFi', 'assets/images/lofi.png', 'Playlist'),
  Album('Synthwave', 'assets/images/synthwave.png', 'Playlist'),
  Album('Focus Beats', 'assets/images/focus_beats.png', 'Playlist'),
  Album('K-Pop Mix', 'assets/images/k-pop.png', 'Playlist'),
];

final List<Album> topGenres = [
  Album('Hip Hop', 'assets/images/hiphop.png', 'Genre'),
  Album('Pop', 'assets/images/pop.png', 'Genre'),
  Album('Indie', 'assets/images/indie.png', 'Genre'),
  Album('Rock', 'assets/images/rock.png', 'Genre'),
];


// -----------------------------------------------------
// HomeScreen을 StatefulWidget으로 변경하고 userName 상태를 추가
// -----------------------------------------------------
class HomeScreen extends StatefulWidget {
  final String userName; // LoginScreen에서 받은 사용자 이름 필드 추가
  // 기본값을 설정하거나, 로그인 화면에서 이름을 전달받도록 합니다.
  const HomeScreen({super.key, this.userName = "User",}); 

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0; // 현재 선택된 탭 인덱스 저장

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: _buildBottomNavBar(context),
      body: CustomScrollView(
        slivers: <Widget>[
          SliverAppBar(
            backgroundColor: Theme.of(context).scaffoldBackgroundColor,
            expandedHeight: 80.0,
            floating: true, 
            pinned: false,
            flexibleSpace: FlexibleSpaceBar( // FlexibleSpaceBar도 const 제거
              titlePadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
              title: Text(
                'Hi, ${widget.userName}', // 사용자 이름 반영
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              centerTitle: false,
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.notifications_none, color: Colors.white),
                onPressed: () {
                  // TODO: 알림 설정 화면으로 이동 로직 구현
                },
              ),
              IconButton(
                icon: const Icon(Icons.settings, color: Colors.white),
                onPressed: () {
                  // TODO: 설정 화면으로 이동 로직 구현
                },
              ),
              const SizedBox(width: 10),
            ],
          ),

          SliverList(
            delegate: SliverChildListDelegate(
              [
                const Padding(
                  padding: EdgeInsets.fromLTRB(20, 20, 20, 10),
                  child: Text(
                    'Your Top Vibes',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                _buildAlbumGrid(topVibes),
                const SizedBox(height: 30),

                const Padding(
                  padding: EdgeInsets.fromLTRB(20, 0, 20, 10),
                  child: Text(
                    'Top Genres',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                _buildHorizontalList(topGenres),
                const SizedBox(height: 100), 
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 앨범 그리드 뷰를 생성하는 함수 (변경 없음)
  Widget _buildAlbumGrid(List<Album> albums) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 15.0,
          mainAxisSpacing: 15.0,
          childAspectRatio: 3.0, 
        ),
        itemCount: albums.length,
        itemBuilder: (context, index) {
          return _AlbumItem(album: albums[index]);
        },
      ),
    );
  }

  // 가로 스크롤 리스트 뷰를 생성하는 함수 (변경 없음)
  Widget _buildHorizontalList(List<Album> albums) {
    return SizedBox(
      height: 200,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 20.0),
        itemCount: albums.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.only(right: 15.0),
            child: _GenreCard(album: albums[index]),
          );
        },
      ),
    );
  }

  // 하단 내비게이션 바 위젯 (로직 수정)
  Widget _buildBottomNavBar(BuildContext context) {
    return BottomNavigationBar(
      backgroundColor: const Color(0xFF282828), 
      selectedItemColor: Colors.white, 
      unselectedItemColor: Colors.grey[600],
      type: BottomNavigationBarType.fixed,
      currentIndex: _currentIndex, // 상태 변수 사용
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.home_filled),
          label: 'Home',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.search),
          label: 'Explore', // SongInputPage로 연결될 탭
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.library_books),
          label: 'Library',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.settings),
          label: 'Premium',
        ),
      ],
      onTap: (index) {
        setState(() {
          _currentIndex = index;
        });

        if (index == 1) { // 'Explore' 탭 (Index 1) 클릭 시
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SongInputPage(userName: widget.userName, ),
            ),
          ).then((_) {
            // SongInputPage에서 돌아왔을 때, 현재 탭을 Home으로 다시 설정 (선택 사항)
            setState(() {
              _currentIndex = 0;
            });
          });
        }
      },
    );
  }
}
// ... (이하 _AlbumItem, _GenreCard 위젯 코드는 동일)
// ----------------------------------------------------------------------------------
// **주의:** SongInputPage 클래스 코드는 이 파일에 포함시키지 않습니다. 
//      SongInputPage 클래스는 이미 'song_input_page.dart'라는 파일에 정의되어 있어야 하며, 
//      이 파일에서는 'song_input_page.dart'를 import하여 사용해야 합니다.
// ----------------------------------------------------------------------------------

// 앨범 아이템 위젯 (print 제거 및 Container 대신 SizedBox 사용)
class _AlbumItem extends StatelessWidget {
  final Album album;

  const _AlbumItem({required this.album});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF282828), 
        borderRadius: BorderRadius.circular(5.0),
      ),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SongScreen(
                songTitle: album.title,
                artistName: 'Various Artists',
                imageUrl: album.imageUrl,
              ),
            ),
          );
          // TODO: 앨범 클릭 이벤트 (음악 재생 시작 또는 상세 화면 이동) 로직 구현
          // print('${album.title} Clicked'); // 🚫 print 제거
        },
        child: Row(
          children: [
            // Container 대신 SizedBox를 사용하여 이미지 크기 명시
            SizedBox( 
              width: 60,
              height: 60,
              child: Image.asset(album.imageUrl, fit: BoxFit.cover, cacheWidth: 200, errorBuilder: (context, error, stackTrace) {
                return Icon(Icons.image, size: 60, color: Colors.grey[400]);
              }),
            ),
            const SizedBox(width: 8),
            // 텍스트
            Flexible(
              child: Text(
                album.title,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// 장르 카드 위젯 (Container 대신 SizedBox 사용)
class _GenreCard extends StatelessWidget {
  final Album album;

  const _GenreCard({required this.album});

  @override
  Widget build(BuildContext context) {
    return SizedBox( // 👈 Container 대신 SizedBox 사용
      width: 150, 
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox( // 👈 Container 대신 SizedBox 사용
            height: 150, 
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8.0),
              child: Image.asset(album.imageUrl, fit: BoxFit.cover, cacheWidth: 200, errorBuilder: (context, error, stackTrace) {
                return Container(
                  color: Colors.grey[800],
                  child: Center(child: Icon(Icons.image, size: 50, color: Colors.grey[400])),
                );
              }),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            album.title,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
            overflow: TextOverflow.ellipsis,
          ),
          Text(
            album.subtitle,
            style: TextStyle(
              color: Colors.grey[500],
              fontSize: 12,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}