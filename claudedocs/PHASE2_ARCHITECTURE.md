# AI 小說生成器 Phase 2 系統架構設計

> **版本**: Phase 2 架構規劃
> **日期**: 2026-01-04
> **狀態**: 設計階段
> **作者**: Claude Code (System Architect)

---

## 目錄

1. [架構概覽](#1-架構概覽)
2. [模組設計](#2-模組設計)
3. [資料結構定義](#3-資料結構定義)
4. [API 接口設計](#4-api-接口設計)
5. [檔案結構設計](#5-檔案結構設計)
6. [資料流程設計](#6-資料流程設計)
7. [實作順序建議](#7-實作順序建議)
8. [測試計劃](#8-測試計劃)
9. [技術選型與依賴](#9-技術選型與依賴)
10. [性能與擴展性](#10-性能與擴展性)

---

## 1. 架構概覽

### 1.1 系統架構圖

```
┌─────────────────────────────────────────────────────────────────────┐
│                          NovelGenerator (主控制器)                    │
│  - 專案管理                                                            │
│  - 生成流程協調                                                        │
│  - enable_phase2 標誌控制                                             │
└───────────┬─────────────────────────────────────────────────────────┘
            │
            ├─────── 現有模組（MVP Phase 1）
            │        ├─ SiliconFlowClient (API 客戶端)
            │        ├─ PromptTemplates (提示詞管理)
            │        └─ JSONParser (容錯解析)
            │
            └─────── 新增模組（Phase 2）
                     │
                     ├─ VolumeManager (分卷管理器)
                     │  ├─ 自動分卷規劃
                     │  ├─ 章節大綱生成
                     │  └─ 劇情節奏控制
                     │
                     ├─ ContextManager (上下文管理器)
                     │  ├─ ChromaDB 向量數據庫
                     │  ├─ RAG 檢索增強
                     │  ├─ 雙層上下文（跨卷 + 卷內）
                     │  └─ 智能上下文壓縮
                     │
                     ├─ PlotManager (劇情節奏管理器)
                     │  ├─ 起承轉合檢測
                     │  ├─ 衝突強度評估
                     │  └─ 節奏曲線生成
                     │
                     └─ ConsistencyChecker (一致性檢查器)
                        ├─ 角色一致性檢查
                        ├─ 時間線驗證
                        └─ 設定衝突檢測

┌─────────────────────────────────────────────────────────────────────┐
│                         資料持久化層                                   │
│  ├─ 專案檔案系統（現有）                                               │
│  │   ├─ metadata.json                                                │
│  │   ├─ outline.txt                                                  │
│  │   └─ chapter_*.txt                                                │
│  │                                                                    │
│  └─ Phase 2 新增檔案                                                  │
│      ├─ volume_plan.json          (分卷規劃)                          │
│      ├─ chapter_outlines.json     (章節大綱)                          │
│      ├─ character_states.json     (角色狀態追蹤)                       │
│      ├─ timeline.json              (時間線記錄)                        │
│      ├─ context_db/                (ChromaDB 向量庫)                  │
│      └─ plots/                     (劇情節奏資料)                      │
│          ├─ plot_curve.json        (節奏曲線)                         │
│          └─ conflict_points.json   (衝突點記錄)                        │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心設計理念

#### 向後兼容性 (Backward Compatibility)
- **enable_phase2 標誌**: 控制是否啟用 Phase 2 功能
- **MVP 模式**: enable_phase2=False 時完全保留 Phase 1 行為
- **增強模式**: enable_phase2=True 時啟用分卷、RAG、一致性檢查

#### 模組化設計 (Modularity)
- 每個管理器獨立職責,可單獨測試
- 統一接口設計,便於擴展和替換
- 鬆耦合架構,降低模組間依賴

#### 可擴展性 (Scalability)
- 支援 100+ 章長篇小說生成
- 向量數據庫支援高效檢索
- 分卷機制降低單次生成複雜度

---

## 2. 模組設計

### 2.1 VolumeManager (分卷管理器)

#### 職責
- 根據總章節數自動規劃分卷
- 為每個分卷生成詳細章節大綱
- 控制劇情節奏和衝突分佈

#### 類別定義

```python
class VolumeManager:
    """分卷管理器 - 負責長篇小說的分卷規劃和章節大綱生成"""

    def __init__(self,
                 project_dir: str,
                 api_client: SiliconFlowClient,
                 prompt_templates: PromptTemplates):
        """
        初始化分卷管理器

        Args:
            project_dir: 專案目錄路徑
            api_client: API 客戶端
            prompt_templates: 提示詞模板
        """
        self.project_dir = project_dir
        self.api_client = api_client
        self.prompt_templates = prompt_templates
        self.volume_plan = None
        self.chapter_outlines = {}

    def create_volume_plan(self,
                          total_chapters: int,
                          outline: str) -> Dict:
        """
        創建分卷計劃

        Args:
            total_chapters: 總章節數
            outline: 整體故事大綱

        Returns:
            分卷計劃字典
            {
                "total_volumes": 3,
                "volumes": [
                    {
                        "volume_id": 1,
                        "name": "序章 - 覺醒",
                        "start_chapter": 1,
                        "end_chapter": 30,
                        "theme": "主角身份建立與初始衝突",
                        "plot_arc": "rising",  # rising/climax/falling
                        "key_events": [...]
                    },
                    ...
                ]
            }
        """
        pass

    def generate_chapter_outlines(self, volume_id: int) -> Dict[int, str]:
        """
        為指定分卷生成詳細章節大綱

        Args:
            volume_id: 分卷編號

        Returns:
            章節大綱字典 {chapter_num: outline_text}
        """
        pass

    def get_volume_by_chapter(self, chapter_num: int) -> Dict:
        """
        根據章節號獲取所屬分卷信息

        Args:
            chapter_num: 章節號

        Returns:
            分卷信息字典
        """
        pass

    def get_chapter_outline(self, chapter_num: int) -> str:
        """
        獲取指定章節的詳細大綱

        Args:
            chapter_num: 章節號

        Returns:
            章節大綱文本
        """
        pass

    def save_volume_plan(self):
        """將分卷計劃保存到 volume_plan.json"""
        pass

    def load_volume_plan(self):
        """從 volume_plan.json 載入分卷計劃"""
        pass
```

#### 與其他模組的交互
- **NovelGenerator**: 接收總體大綱,返回分卷計劃
- **PlotManager**: 提供分卷劇情走向,接收節奏建議
- **PromptTemplates**: 調用提示詞生成章節大綱

---

### 2.2 ContextManager (上下文管理器)

#### 職責
- 管理雙層上下文（跨卷全局 + 卷內局部）
- 使用 ChromaDB 實現語義化檢索
- 智能壓縮上下文以滿足 Token 限制

#### 類別定義

```python
class ContextManager:
    """上下文管理器 - RAG 檢索增強與雙層上下文管理"""

    def __init__(self,
                 project_dir: str,
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        初始化上下文管理器

        Args:
            project_dir: 專案目錄路徑
            embedding_model: 嵌入模型名稱
        """
        self.project_dir = project_dir
        self.db_path = os.path.join(project_dir, "context_db")

        # 初始化 ChromaDB 客戶端
        self.chroma_client = chromadb.PersistentClient(path=self.db_path)
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )

        # 兩個 Collection: 全局 + 卷內
        self.global_collection = None
        self.volume_collection = None

    def initialize_collections(self):
        """初始化或載入向量數據庫 Collection"""
        pass

    def add_chapter_to_context(self,
                               chapter_num: int,
                               chapter_content: str,
                               volume_id: int,
                               metadata: Dict):
        """
        將章節內容添加到向量庫

        Args:
            chapter_num: 章節號
            chapter_content: 章節文本
            volume_id: 所屬分卷ID
            metadata: 元數據（角色、事件等）
        """
        pass

    def retrieve_global_context(self,
                                query: str,
                                top_k: int = 3) -> List[Dict]:
        """
        從全局上下文檢索相關內容

        Args:
            query: 查詢文本（如"主角當前狀態"）
            top_k: 返回前 k 個最相關結果

        Returns:
            相關內容列表
            [
                {
                    "chapter_num": 15,
                    "content": "...",
                    "distance": 0.23,
                    "metadata": {...}
                },
                ...
            ]
        """
        pass

    def retrieve_volume_context(self,
                               volume_id: int,
                               query: str,
                               top_k: int = 5) -> List[Dict]:
        """
        從指定分卷內檢索相關內容

        Args:
            volume_id: 分卷ID
            query: 查詢文本
            top_k: 返回數量

        Returns:
            相關內容列表
        """
        pass

    def build_chapter_context(self,
                             chapter_num: int,
                             volume_id: int,
                             max_tokens: int = 2000) -> str:
        """
        為生成章節構建完整上下文

        策略:
        1. 檢索全局關鍵信息（角色設定、世界觀）
        2. 檢索卷內劇情線索
        3. 附加上一章結尾
        4. 智能壓縮到 max_tokens 限制內

        Args:
            chapter_num: 當前章節號
            volume_id: 所屬分卷
            max_tokens: Token 上限

        Returns:
            組合後的上下文文本
        """
        pass

    def compress_context(self,
                        context_pieces: List[str],
                        max_tokens: int) -> str:
        """
        智能壓縮上下文

        策略:
        1. 優先保留最近章節
        2. 摘要提取關鍵信息
        3. 移除冗餘描述

        Args:
            context_pieces: 上下文片段列表
            max_tokens: Token 限制

        Returns:
            壓縮後的上下文
        """
        pass

    def clear_volume_context(self, volume_id: int):
        """清除指定分卷的上下文緩存"""
        pass
```

#### 與其他模組的交互
- **NovelGenerator**: 為章節生成提供上下文
- **VolumeManager**: 獲取分卷範圍信息
- **ConsistencyChecker**: 提供歷史內容檢索

---

### 2.3 PlotManager (劇情節奏管理器)

#### 職責
- 分析劇情節奏（起承轉合）
- 評估衝突強度
- 生成劇情曲線並給出建議

#### 類別定義

```python
class PlotManager:
    """劇情節奏管理器 - 控制故事節奏與衝突分佈"""

    # 節奏類型枚舉
    class PlotPhase(Enum):
        INTRODUCTION = "起"  # 開場鋪墊
        DEVELOPMENT = "承"   # 劇情發展
        TWIST = "轉"         # 轉折高潮
        RESOLUTION = "合"    # 收尾總結

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.plot_curve = []  # 劇情曲線數據點
        self.conflict_points = {}  # 衝突點記錄

    def calculate_plot_phase(self,
                            chapter_num: int,
                            total_chapters: int,
                            volume_position: str = None) -> PlotPhase:
        """
        計算當前章節應處於的劇情階段

        規則:
        - 整體小說: 前25%為起, 25-60%為承, 60-85%為轉, 85%後為合
        - 單個分卷: 同樣遵循起承轉合比例

        Args:
            chapter_num: 章節號
            total_chapters: 總章節數
            volume_position: 在分卷中的位置 ("start"/"middle"/"end")

        Returns:
            PlotPhase 枚舉值
        """
        pass

    def calculate_conflict_intensity(self,
                                    chapter_num: int,
                                    plot_phase: PlotPhase,
                                    volume_arc: str) -> float:
        """
        計算期望的衝突強度 (0.0-1.0)

        策略:
        - 起階段: 0.3-0.5 (低強度,建立衝突)
        - 承階段: 0.5-0.7 (中強度,推進劇情)
        - 轉階段: 0.7-1.0 (高強度,高潮迭起)
        - 合階段: 0.4-0.6 (降低,解決衝突)

        Args:
            chapter_num: 章節號
            plot_phase: 劇情階段
            volume_arc: 分卷劇情曲線類型 ("rising"/"climax"/"falling")

        Returns:
            期望衝突強度值
        """
        pass

    def generate_plot_guidance(self,
                              chapter_num: int,
                              total_chapters: int,
                              volume_info: Dict) -> Dict:
        """
        為章節生成劇情指導建議

        Returns:
            {
                "plot_phase": "承",
                "conflict_intensity": 0.65,
                "guidance": [
                    "推進主線劇情,深化角色衝突",
                    "引入次要情節線",
                    "為下一章埋下伏筆"
                ],
                "avoid": [
                    "避免過早解決主要衝突",
                    "不宜引入過多新角色"
                ]
            }
        """
        pass

    def analyze_chapter_plot(self, chapter_content: str) -> Dict:
        """
        分析已生成章節的劇情特徵（可選,未來使用 AI 分析）

        Args:
            chapter_content: 章節文本

        Returns:
            {
                "detected_phase": "承",
                "conflict_score": 0.6,
                "key_events": [...],
                "warnings": [...]  # 如果偏離預期節奏
            }
        """
        pass

    def save_plot_curve(self):
        """保存劇情曲線到 plots/plot_curve.json"""
        pass

    def load_plot_curve(self):
        """載入劇情曲線數據"""
        pass
```

#### 與其他模組的交互
- **VolumeManager**: 獲取分卷劇情定位
- **PromptTemplates**: 提供劇情指導給提示詞
- **ConsistencyChecker**: 檢測劇情是否符合預期節奏

---

### 2.4 ConsistencyChecker (一致性檢查器)

#### 職責
- 角色性格、設定一致性檢查
- 時間線邏輯驗證
- 設定衝突自動檢測

#### 類別定義

```python
class ConsistencyChecker:
    """一致性檢查器 - 確保角色、設定、時間線的連貫性"""

    def __init__(self,
                 project_dir: str,
                 context_manager: ContextManager):
        self.project_dir = project_dir
        self.context_manager = context_manager

        # 載入追蹤資料
        self.character_states = {}  # 角色狀態追蹤
        self.timeline = []          # 時間線記錄
        self.world_settings = {}    # 世界觀設定

    def track_character_state(self,
                             chapter_num: int,
                             character_name: str,
                             state_updates: Dict):
        """
        追蹤角色狀態變化

        Args:
            chapter_num: 章節號
            character_name: 角色名稱
            state_updates: 狀態更新
                {
                    "location": "星際基地-阿爾法區",
                    "status": "受傷",
                    "relationships": {"角色B": "盟友"},
                    "possessions": ["能量劍", "通訊器"]
                }
        """
        pass

    def check_character_consistency(self,
                                   chapter_num: int,
                                   chapter_content: str) -> List[Dict]:
        """
        檢查角色一致性

        檢查項:
        1. 角色是否突然改變性格
        2. 角色位置是否合理
        3. 已死亡角色是否復活
        4. 關係設定是否矛盾

        Returns:
            警告列表
            [
                {
                    "type": "character_inconsistency",
                    "severity": "warning/error",
                    "character": "角色A",
                    "message": "角色A在第10章已死亡,但在本章出現",
                    "suggestion": "修改劇情或復活設定"
                },
                ...
            ]
        """
        pass

    def track_timeline(self,
                      chapter_num: int,
                      time_info: Dict):
        """
        記錄時間線

        Args:
            chapter_num: 章節號
            time_info: 時間信息
                {
                    "date": "星曆 2157年3月15日",
                    "duration": "3天",
                    "events": ["主角抵達基地", "遭遇襲擊"]
                }
        """
        pass

    def check_timeline_consistency(self,
                                  chapter_num: int,
                                  chapter_content: str) -> List[Dict]:
        """
        檢查時間線邏輯

        檢查項:
        1. 時間是否倒流
        2. 事件順序是否合理
        3. 角色年齡是否符合

        Returns:
            警告列表（格式同上）
        """
        pass

    def track_world_setting(self,
                           setting_type: str,
                           setting_name: str,
                           setting_value: Any):
        """
        記錄世界觀設定

        Args:
            setting_type: 設定類型 ("technology"/"magic"/"geography"等)
            setting_name: 設定名稱
            setting_value: 設定值
        """
        pass

    def check_setting_consistency(self,
                                 chapter_content: str) -> List[Dict]:
        """
        檢查設定一致性

        檢查項:
        1. 科技設定是否矛盾
        2. 地理設定是否衝突
        3. 規則設定是否違背

        Returns:
            警告列表
        """
        pass

    def run_full_check(self,
                      chapter_num: int,
                      chapter_content: str) -> Dict:
        """
        運行完整一致性檢查

        Returns:
            {
                "passed": True/False,
                "warnings": [...],
                "errors": [...],
                "suggestions": [...]
            }
        """
        pass

    def save_tracking_data(self):
        """保存角色狀態、時間線、設定到對應 JSON 檔案"""
        pass

    def load_tracking_data(self):
        """載入追蹤資料"""
        pass
```

#### 與其他模組的交互
- **ContextManager**: 檢索歷史章節內容進行比對
- **NovelGenerator**: 生成後觸發一致性檢查
- **VolumeManager**: 獲取章節大綱作為檢查依據

---

## 3. 資料結構定義

### 3.1 volume_plan.json (分卷計劃)

```json
{
  "version": "2.0",
  "created_at": "2026-01-04T14:30:00Z",
  "total_chapters": 100,
  "total_volumes": 3,
  "volumes": [
    {
      "volume_id": 1,
      "name": "序章 - 覺醒",
      "start_chapter": 1,
      "end_chapter": 30,
      "chapter_count": 30,
      "theme": "主角身份建立與初始衝突設置",
      "plot_arc": "rising",
      "target_word_count": 90000,
      "key_events": [
        "主角發現能力",
        "初遇導師",
        "第一次戰鬥",
        "揭露組織陰謀"
      ],
      "main_characters": ["主角", "導師", "反派A"],
      "settings_introduced": [
        "未來都市背景",
        "能力系統設定",
        "組織結構"
      ],
      "conflicts": {
        "internal": "主角身份認同危機",
        "external": "與組織的初步對抗"
      }
    },
    {
      "volume_id": 2,
      "name": "中卷 - 試煉",
      "start_chapter": 31,
      "end_chapter": 70,
      "chapter_count": 40,
      "theme": "能力成長與多方勢力博弈",
      "plot_arc": "climax",
      "target_word_count": 120000,
      "key_events": [
        "主角修煉突破",
        "盟友背叛",
        "重大秘密揭露",
        "決戰前夕"
      ],
      "main_characters": ["主角", "盟友團隊", "反派B", "神秘人"],
      "settings_introduced": [
        "古代遺跡",
        "其他勢力體系",
        "歷史真相"
      ],
      "conflicts": {
        "internal": "信任與懷疑的掙扎",
        "external": "多方勢力圍剿"
      }
    },
    {
      "volume_id": 3,
      "name": "終章 - 終焉與新生",
      "start_chapter": 71,
      "end_chapter": 100,
      "chapter_count": 30,
      "target_word_count": 90000,
      "theme": "最終決戰與世界重構",
      "plot_arc": "falling",
      "key_events": [
        "最終 BOSS 戰",
        "主角覺醒",
        "世界觀顛覆",
        "結局與後日談"
      ],
      "main_characters": ["主角", "核心團隊", "終極反派"],
      "settings_introduced": [
        "真相揭示",
        "新秩序建立"
      ],
      "conflicts": {
        "internal": "終極選擇與犧牲",
        "external": "終極對決"
      }
    }
  ],
  "plot_transitions": [
    {
      "from_volume": 1,
      "to_volume": 2,
      "transition_chapter": 30,
      "transition_event": "導師犧牲,主角決心復仇並揭開真相"
    },
    {
      "from_volume": 2,
      "to_volume": 3,
      "transition_chapter": 70,
      "transition_event": "終極反派現身,世界面臨毀滅危機"
    }
  ]
}
```

### 3.2 chapter_outlines.json (章節大綱)

```json
{
  "version": "2.0",
  "created_at": "2026-01-04T14:35:00Z",
  "volume_id": 1,
  "outlines": {
    "1": {
      "chapter_num": 1,
      "title": "平凡的一天",
      "plot_phase": "起",
      "conflict_intensity": 0.3,
      "summary": "展示主角的日常生活,埋下能力覺醒的伏筆",
      "key_scenes": [
        "主角上班途中的意外事件",
        "發現異常現象",
        "初次感知到能力"
      ],
      "characters_appear": ["主角", "同事A", "路人"],
      "locations": ["都市街道", "辦公室"],
      "plot_points": [
        "引入主角背景設定",
        "設置懸念（異常現象）",
        "為下一章埋下伏筆（能力覺醒）"
      ],
      "word_count_target": 3000,
      "mood": "平靜中透露不安",
      "pacing": "緩慢開場,結尾加速"
    },
    "2": {
      "chapter_num": 2,
      "title": "覺醒",
      "plot_phase": "起",
      "conflict_intensity": 0.5,
      "summary": "主角能力正式覺醒,遭遇第一次危險",
      "key_scenes": [
        "能力突然爆發",
        "被神秘組織發現",
        "逃脫與追逐"
      ],
      "characters_appear": ["主角", "組織追兵", "導師（遠觀）"],
      "locations": ["都市暗巷", "廢棄工廠"],
      "plot_points": [
        "能力系統初步展示",
        "引入反派勢力",
        "導師登場暗示"
      ],
      "word_count_target": 3200,
      "mood": "緊張刺激",
      "pacing": "快節奏動作戲"
    }
  }
}
```

### 3.3 character_states.json (角色狀態追蹤)

```json
{
  "version": "2.0",
  "last_updated": "2026-01-04T15:00:00Z",
  "characters": {
    "主角-林宇": {
      "first_appearance": 1,
      "last_appearance": 45,
      "current_status": "alive",
      "timeline": [
        {
          "chapter": 1,
          "age": 25,
          "location": "新東京都",
          "status": "普通上班族",
          "abilities": [],
          "relationships": {},
          "possessions": ["智能手環", "公寓鑰匙"]
        },
        {
          "chapter": 2,
          "age": 25,
          "location": "新東京都-廢棄工廠",
          "status": "能力覺醒",
          "abilities": ["時間暫停-初級"],
          "relationships": {
            "組織": "敵對",
            "導師（未知名）": "觀察中"
          },
          "possessions": ["智能手環", "能量結晶（拾取）"]
        },
        {
          "chapter": 10,
          "age": 25,
          "location": "地下基地",
          "status": "接受訓練",
          "abilities": ["時間暫停-中級", "時間回溯-初級"],
          "relationships": {
            "導師-陳墨": "師徒",
            "組織": "通緝中",
            "盟友-蘇雨": "信任"
          },
          "possessions": ["智能手環", "能量結晶", "古代時鐘"]
        }
      ],
      "personality_traits": [
        "謹慎",
        "正義感強",
        "學習能力快"
      ],
      "key_decisions": [
        {
          "chapter": 5,
          "decision": "選擇跟隨導師學習",
          "consequence": "進入地下組織,脫離正常生活"
        }
      ]
    },
    "導師-陳墨": {
      "first_appearance": 3,
      "last_appearance": 30,
      "current_status": "deceased",
      "death_chapter": 30,
      "death_cause": "為保護主角犧牲",
      "timeline": [
        {
          "chapter": 3,
          "age": 50,
          "location": "未知",
          "status": "神秘觀察者",
          "abilities": ["時間操控-大師級"],
          "relationships": {
            "主角-林宇": "觀察目標"
          }
        }
      ]
    }
  }
}
```

### 3.4 timeline.json (時間線記錄)

```json
{
  "version": "2.0",
  "last_updated": "2026-01-04T15:10:00Z",
  "story_timeline": {
    "start_date": "2157年3月1日",
    "current_date": "2157年5月20日",
    "total_story_days": 80,
    "events": [
      {
        "chapter": 1,
        "date": "2157年3月1日",
        "day_of_story": 1,
        "duration_days": 1,
        "events": [
          "主角日常生活",
          "發現異常現象"
        ],
        "time_notes": "故事開始日"
      },
      {
        "chapter": 2,
        "date": "2157年3月2日",
        "day_of_story": 2,
        "duration_days": 1,
        "events": [
          "能力覺醒",
          "遭遇組織追殺",
          "逃脫成功"
        ],
        "time_notes": "能力覺醒日"
      },
      {
        "chapter": 3,
        "date": "2157年3月3日",
        "day_of_story": 3,
        "duration_days": 1,
        "events": [
          "導師現身",
          "初步了解能力體系"
        ]
      },
      {
        "chapter": 4-10,
        "date": "2157年3月4日 - 3月20日",
        "day_of_story": 4,
        "duration_days": 17,
        "events": [
          "接受導師訓練",
          "能力提升"
        ],
        "time_notes": "訓練期"
      }
    ],
    "time_skips": [
      {
        "from_chapter": 10,
        "to_chapter": 11,
        "skip_duration": "3個月",
        "reason": "訓練期跳過日常重複內容"
      }
    ],
    "warnings": []
  }
}
```

---

## 4. API 接口設計

### 4.1 NovelGenerator (主控制器擴展)

```python
class NovelGenerator:
    """小說生成器 - Phase 2 擴展版本"""

    def __init__(self,
                 api_key: str,
                 model: str = None,
                 enable_phase2: bool = False):
        """
        初始化生成器

        Args:
            api_key: API Key
            model: 模型名稱
            enable_phase2: 是否啟用 Phase 2 功能
        """
        # Phase 1 原有初始化
        self.api_client = SiliconFlowClient(api_key, model)
        self.prompt_templates = PromptTemplates()

        # Phase 2 新增初始化
        self.enable_phase2 = enable_phase2
        if enable_phase2:
            self.volume_manager = None
            self.context_manager = None
            self.plot_manager = None
            self.consistency_checker = None

    def create_project(self,
                      title: str,
                      genre: str,
                      theme: str,
                      total_chapters: int,
                      enable_volume_split: bool = None):
        """
        建立專案 - Phase 2 擴展版本

        Args:
            title: 小說標題
            genre: 類型
            theme: 主題
            total_chapters: 總章節數
            enable_volume_split: 是否啟用分卷（None 時自動判斷）
        """
        # Phase 1 原有邏輯
        # ...

        # Phase 2 擴展邏輯
        if self.enable_phase2:
            # 自動判斷是否需要分卷
            if enable_volume_split is None:
                enable_volume_split = total_chapters >= 30

            if enable_volume_split:
                self._initialize_phase2_managers()

    def _initialize_phase2_managers(self):
        """初始化 Phase 2 所有管理器"""
        self.volume_manager = VolumeManager(
            self.project_dir,
            self.api_client,
            self.prompt_templates
        )

        self.context_manager = ContextManager(self.project_dir)
        self.context_manager.initialize_collections()

        self.plot_manager = PlotManager(self.project_dir)

        self.consistency_checker = ConsistencyChecker(
            self.project_dir,
            self.context_manager
        )

    def generate_outline(self) -> str:
        """
        生成大綱 - Phase 2 增強版本

        返回:
            總體大綱文本
        """
        # Phase 1 原有邏輯生成總體大綱
        outline = self._generate_base_outline()

        # Phase 2 擴展: 如果啟用分卷,生成分卷計劃
        if self.enable_phase2 and self.volume_manager:
            print("⏳ 正在生成分卷計劃...")
            self.volume_manager.create_volume_plan(
                total_chapters=self.metadata['total_chapters'],
                outline=outline
            )
            self.volume_manager.save_volume_plan()
            print("✓ 分卷計劃已生成\n")

        return outline

    def generate_chapter(self, chapter_num: int) -> Dict:
        """
        生成章節 - Phase 2 增強版本

        Args:
            chapter_num: 章節號

        Returns:
            章節信息字典
        """
        if not self.enable_phase2:
            # Phase 1 原有邏輯
            return self._generate_chapter_phase1(chapter_num)

        # Phase 2 增強邏輯
        print(f"⏳ 正在生成第 {chapter_num} 章（Phase 2 模式）...")

        # 1. 獲取分卷信息
        volume_info = self.volume_manager.get_volume_by_chapter(chapter_num)
        chapter_outline = self.volume_manager.get_chapter_outline(chapter_num)

        # 2. 構建增強上下文
        enhanced_context = self.context_manager.build_chapter_context(
            chapter_num=chapter_num,
            volume_id=volume_info['volume_id'],
            max_tokens=2000
        )

        # 3. 獲取劇情指導
        plot_guidance = self.plot_manager.generate_plot_guidance(
            chapter_num=chapter_num,
            total_chapters=self.metadata['total_chapters'],
            volume_info=volume_info
        )

        # 4. 構建增強提示詞
        prompt = self.prompt_templates.build_chapter_prompt_phase2(
            chapter_num=chapter_num,
            total_chapters=self.metadata['total_chapters'],
            chapter_outline=chapter_outline,
            enhanced_context=enhanced_context,
            plot_guidance=plot_guidance
        )

        # 5. 調用 API 生成
        result = self.api_client.generate(
            prompt=prompt,
            temperature=0.8,
            max_tokens=5000
        )

        chapter_content = result['content']

        # 6. 保存章節
        chapter_file = os.path.join(
            self.project_dir,
            f"chapter_{chapter_num:03d}.txt"
        )
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(chapter_content)

        # 7. 添加到上下文數據庫
        self.context_manager.add_chapter_to_context(
            chapter_num=chapter_num,
            chapter_content=chapter_content,
            volume_id=volume_info['volume_id'],
            metadata={
                'outline': chapter_outline,
                'plot_phase': plot_guidance['plot_phase']
            }
        )

        # 8. 一致性檢查
        print("⏳ 執行一致性檢查...")
        check_result = self.consistency_checker.run_full_check(
            chapter_num=chapter_num,
            chapter_content=chapter_content
        )

        if not check_result['passed']:
            print(f"⚠️  一致性檢查發現 {len(check_result['warnings'])} 個警告")
            for warning in check_result['warnings']:
                print(f"   - {warning['message']}")

        print(f"✓ 第 {chapter_num} 章完成（{len(chapter_content)} 字）\n")

        return {
            'chapter_num': chapter_num,
            'word_count': len(chapter_content),
            'file_path': chapter_file,
            'consistency_check': check_result,
            **result
        }
```

### 4.2 PromptTemplates 擴展

```python
class PromptTemplates:
    """提示詞模板 - Phase 2 擴展"""

    @staticmethod
    def build_volume_plan_prompt(total_chapters: int,
                                 outline: str,
                                 genre: str,
                                 theme: str) -> str:
        """
        構建分卷計劃生成提示詞

        Args:
            total_chapters: 總章節數
            outline: 總體大綱
            genre: 類型
            theme: 主題

        Returns:
            分卷計劃提示詞
        """
        return f"""你是專業小說編輯,請為以下長篇小說設計分卷計劃。

【小說信息】
- 類型: {genre}
- 主題: {theme}
- 總章節數: {total_chapters}

【總體大綱】
{outline}

【分卷規劃要求】
1. 根據總章節數決定分卷數量:
   - 30-50章: 建議2卷
   - 51-80章: 建議3卷
   - 81-120章: 建議3-4卷
   - 120章以上: 建議4-5卷

2. 每個分卷需包含:
   - 分卷名稱（體現主題）
   - 章節範圍
   - 劇情定位（rising/climax/falling）
   - 核心主題
   - 主要事件列表
   - 主要角色
   - 引入的設定

3. 確保分卷間劇情曲線合理:
   - 第1卷: 鋪墊與衝突建立
   - 中間卷: 推進與高潮
   - 最後1卷: 解決與收尾

請以 JSON 格式輸出分卷計劃:
```json
{{
  "total_volumes": 3,
  "volumes": [...]
}}
```
"""

    @staticmethod
    def build_chapter_outline_prompt(volume_info: Dict,
                                     chapter_num: int,
                                     overall_outline: str) -> str:
        """
        構建單章大綱生成提示詞

        Args:
            volume_info: 分卷信息
            chapter_num: 章節號
            overall_outline: 總體大綱

        Returns:
            章節大綱提示詞
        """
        return f"""請為第 {chapter_num} 章生成詳細大綱。

【分卷信息】
- 分卷名稱: {volume_info['name']}
- 分卷主題: {volume_info['theme']}
- 章節範圍: {volume_info['start_chapter']}-{volume_info['end_chapter']}
- 劇情定位: {volume_info['plot_arc']}

【總體大綱】
{overall_outline}

【要求】
1. 明確本章在分卷中的位置和作用
2. 列出 3-5 個關鍵場景
3. 指定登場角色
4. 說明本章推進的劇情點
5. 設定期望字數和節奏

請以 JSON 格式輸出:
```json
{{
  "chapter_num": {chapter_num},
  "title": "章節標題",
  "summary": "一句話概述",
  "key_scenes": [...],
  "characters_appear": [...],
  "plot_points": [...],
  ...
}}
```
"""

    @staticmethod
    def build_chapter_prompt_phase2(chapter_num: int,
                                   total_chapters: int,
                                   chapter_outline: str,
                                   enhanced_context: str,
                                   plot_guidance: Dict) -> str:
        """
        構建 Phase 2 增強章節生成提示詞

        Args:
            chapter_num: 章節號
            total_chapters: 總章節數
            chapter_outline: 本章詳細大綱
            enhanced_context: RAG 檢索的增強上下文
            plot_guidance: 劇情指導建議

        Returns:
            完整提示詞
        """
        return f"""你是專業小說作家,正在創作第 {chapter_num}/{total_chapters} 章。

【核心規則】
{PromptTemplates.SYSTEM_CORE}

【本章大綱】
{chapter_outline}

【相關上下文】（基於前文檢索）
{enhanced_context}

【劇情指導】
- 劇情階段: {plot_guidance['plot_phase']}
- 衝突強度: {plot_guidance['conflict_intensity']:.1f}/1.0
- 創作建議: {', '.join(plot_guidance['guidance'])}
- 注意事項: {', '.join(plot_guidance['avoid'])}

【格式要求】
{PromptTemplates.FORMAT_RULES}

【一致性要求】
{PromptTemplates.CONSISTENCY_RULES}

現在開始創作第 {chapter_num} 章,字數 2500-3500 字:
"""
```

---

## 5. 檔案結構設計

### 5.1 完整目錄樹

```
novel_時空裂痕_20260104_143140/
├── metadata.json                    # 專案元數據（Phase 1）
├── outline.txt                      # 總體大綱（Phase 1）
│
├── volume_plan.json                 # 分卷計劃（Phase 2 新增）
├── chapter_outlines.json            # 詳細章節大綱（Phase 2 新增）
├── character_states.json            # 角色狀態追蹤（Phase 2 新增）
├── timeline.json                    # 時間線記錄（Phase 2 新增）
│
├── context_db/                      # ChromaDB 向量數據庫（Phase 2 新增）
│   ├── chroma.sqlite3              # SQLite 後端
│   ├── global_context/             # 全局上下文 Collection
│   └── volume_1_context/           # 分卷上下文 Collection
│
├── plots/                           # 劇情節奏資料（Phase 2 新增）
│   ├── plot_curve.json             # 劇情曲線數據
│   └── conflict_points.json        # 衝突點記錄
│
├── chapters/                        # 章節文件目錄（可選組織）
│   ├── volume_1/
│   │   ├── chapter_001.txt
│   │   ├── chapter_002.txt
│   │   └── ...
│   ├── volume_2/
│   │   ├── chapter_031.txt
│   │   └── ...
│   └── volume_3/
│       └── ...
│
├── chapter_001.txt                  # 第 1 章（Phase 1 兼容）
├── chapter_002.txt                  # 第 2 章
├── ...
├── chapter_100.txt                  # 第 100 章
│
├── full_novel.txt                   # 完整小說合併（Phase 1）
│
└── logs/                            # 生成日誌（可選）
    ├── generation.log              # 生成過程日誌
    └── consistency_checks.log      # 一致性檢查日誌
```

### 5.2 檔案用途說明

| 檔案/目錄 | Phase | 用途 | 更新時機 |
|----------|-------|------|---------|
| `metadata.json` | 1 | 專案基本信息 | 專案創建時 |
| `outline.txt` | 1 | 總體故事大綱 | 大綱生成時 |
| `volume_plan.json` | 2 | 分卷規劃詳情 | 大綱生成後（Phase 2） |
| `chapter_outlines.json` | 2 | 每章詳細大綱 | 分卷規劃後 |
| `character_states.json` | 2 | 角色狀態追蹤 | 每章生成後更新 |
| `timeline.json` | 2 | 時間線記錄 | 每章生成後更新 |
| `context_db/` | 2 | 向量數據庫 | 每章生成後添加 |
| `plots/` | 2 | 劇情節奏數據 | 章節生成時記錄 |
| `chapter_*.txt` | 1 | 章節文本 | 章節生成時 |
| `full_novel.txt` | 1 | 完整小說 | 所有章節完成後 |

---

## 6. 資料流程設計

### 6.1 Phase 2 完整生成流程

```
用戶輸入
  ↓
[1] NovelGenerator.create_project()
  ├─ 創建專案目錄
  ├─ 保存 metadata.json
  └─ 判斷是否啟用 Phase 2（total_chapters >= 30）
      ├─ Yes → 初始化 Phase 2 管理器
      │         ├─ VolumeManager
      │         ├─ ContextManager（初始化 ChromaDB）
      │         ├─ PlotManager
      │         └─ ConsistencyChecker
      └─ No → 使用 Phase 1 模式
  ↓
[2] NovelGenerator.generate_outline()
  ├─ 調用 API 生成總體大綱
  ├─ 保存 outline.txt
  └─ 如果 Phase 2:
      ├─ VolumeManager.create_volume_plan()
      │   ├─ 調用 AI 分析大綱
      │   ├─ 規劃分卷數量和範圍
      │   └─ 保存 volume_plan.json
      └─ 為每個分卷生成章節大綱
          ├─ VolumeManager.generate_chapter_outlines(volume_id)
          └─ 保存 chapter_outlines.json
  ↓
[3] NovelGenerator.generate_all_chapters()
  ├─ for chapter_num in 1..total_chapters:
  │   ↓
  │   [3.1] 獲取分卷信息
  │   │   └─ VolumeManager.get_volume_by_chapter(chapter_num)
  │   ↓
  │   [3.2] 獲取章節大綱
  │   │   └─ VolumeManager.get_chapter_outline(chapter_num)
  │   ↓
  │   [3.3] 構建增強上下文
  │   │   └─ ContextManager.build_chapter_context()
  │   │       ├─ 檢索全局關鍵信息（角色、世界觀）
  │   │       ├─ 檢索卷內劇情線索
  │   │       ├─ 讀取上一章結尾
  │   │       └─ 智能壓縮到 Token 限制
  │   ↓
  │   [3.4] 生成劇情指導
  │   │   └─ PlotManager.generate_plot_guidance()
  │   │       ├─ 計算劇情階段（起/承/轉/合）
  │   │       ├─ 評估期望衝突強度
  │   │       └─ 生成創作建議
  │   ↓
  │   [3.5] 構建提示詞
  │   │   └─ PromptTemplates.build_chapter_prompt_phase2()
  │   │       ├─ 核心規則
  │   │       ├─ 本章大綱
  │   │       ├─ 增強上下文
  │   │       ├─ 劇情指導
  │   │       └─ 一致性要求
  │   ↓
  │   [3.6] 調用 API 生成章節
  │   │   └─ SiliconFlowClient.generate()
  │   ↓
  │   [3.7] 保存章節文件
  │   │   └─ chapter_XXX.txt
  │   ↓
  │   [3.8] 添加到向量數據庫
  │   │   └─ ContextManager.add_chapter_to_context()
  │   │       ├─ 分段嵌入（每 500 字一段）
  │   │       ├─ 添加到 global_collection
  │   │       └─ 添加到 volume_X_collection
  │   ↓
  │   [3.9] 執行一致性檢查
  │   │   └─ ConsistencyChecker.run_full_check()
  │   │       ├─ 角色一致性檢查
  │   │       ├─ 時間線驗證
  │   │       ├─ 設定衝突檢測
  │   │       └─ 生成警告報告
  │   ↓
  │   [3.10] 更新追蹤資料
  │   │   ├─ 角色狀態 → character_states.json
  │   │   ├─ 時間線 → timeline.json
  │   │   └─ 劇情曲線 → plots/plot_curve.json
  │   ↓
  │   └─ 進入下一章
  ↓
[4] NovelGenerator.merge_chapters()
  ├─ 合併所有章節到 full_novel.txt
  └─ 生成最終統計報告
  ↓
完成 ✓
```

### 6.2 關鍵決策點

#### 決策點 1: 是否啟用 Phase 2？
```python
def _should_enable_phase2(total_chapters: int) -> bool:
    """
    自動判斷是否啟用 Phase 2

    規則:
    - total_chapters < 30: 不啟用（MVP 模式足夠）
    - 30 <= total_chapters < 50: 建議啟用（用戶可選）
    - total_chapters >= 50: 強制啟用（必要性）
    """
    if total_chapters < 30:
        return False
    elif total_chapters < 50:
        user_choice = input("檢測到較長篇章,是否啟用 Phase 2 增強功能? [Y/n]: ")
        return user_choice.lower() != 'n'
    else:
        print("⚠️  檢測到長篇小說,自動啟用 Phase 2 功能")
        return True
```

#### 決策點 2: 分卷數量決策
```python
def _calculate_volume_count(total_chapters: int) -> int:
    """
    計算建議分卷數量

    規則:
    - 30-50章: 2卷
    - 51-80章: 3卷
    - 81-120章: 4卷
    - 120+章: 5卷
    """
    if total_chapters <= 50:
        return 2
    elif total_chapters <= 80:
        return 3
    elif total_chapters <= 120:
        return 4
    else:
        return 5
```

#### 決策點 3: 上下文壓縮策略
```python
def _compress_context_strategy(context_pieces: List[str],
                               max_tokens: int) -> str:
    """
    上下文壓縮策略選擇

    優先級:
    1. 上一章結尾（必須保留,1000字）
    2. 角色核心設定（檢索 top-3）
    3. 世界觀設定（檢索 top-2）
    4. 卷內關鍵事件（檢索 top-3）
    5. 剩餘 token 分配給其他檢索結果
    """
    reserved = {
        'previous_chapter': 1000,  # 字數
        'characters': 500,
        'world_settings': 300,
        'key_events': 400
    }
    # 實際壓縮邏輯...
```

---

## 7. 實作順序建議

### Phase 2.1: 分卷 + 章節大綱 (預計 1 週)

#### 任務列表

**Day 1-2: VolumeManager 基礎實現**
- [ ] 創建 `core/volume_manager.py`
- [ ] 實現 `create_volume_plan()` 方法
- [ ] 實現 `generate_chapter_outlines()` 方法
- [ ] 實現 `save/load_volume_plan()` 方法
- [ ] 單元測試: 測試 30/50/100 章的分卷規劃

**Day 3-4: 提示詞擴展**
- [ ] 擴展 `PromptTemplates` 類別
- [ ] 實現 `build_volume_plan_prompt()`
- [ ] 實現 `build_chapter_outline_prompt()`
- [ ] 測試提示詞生成質量

**Day 5-6: NovelGenerator 集成**
- [ ] 修改 `NovelGenerator.__init__()` 添加 `enable_phase2` 參數
- [ ] 修改 `generate_outline()` 整合分卷邏輯
- [ ] 實現 `_should_enable_phase2()` 判斷邏輯
- [ ] 端到端測試: 生成 50 章小說的分卷計劃

**Day 7: 測試與文檔**
- [ ] 完整測試 Phase 2.1 功能
- [ ] 編寫使用範例
- [ ] 更新 README.md

#### 里程碑驗收標準
- ✅ 能夠自動為 100 章小說生成 3-4 個分卷
- ✅ 每個分卷有明確的主題和章節範圍
- ✅ 每章有詳細的劇情大綱（300-500 字）
- ✅ 分卷計劃保存為 JSON 可被載入
- ✅ 通過 30/50/100 章的測試案例

#### 依賴關係
- **前置**: MVP Phase 1 完成
- **並行**: 無
- **後置**: Phase 2.2 RAG 實現

---

### Phase 2.2: RAG + 雙層上下文 (預計 1 週)

#### 任務列表

**Day 1-2: ChromaDB 集成**
- [ ] 安裝依賴: `chromadb`, `sentence-transformers`
- [ ] 創建 `core/context_manager.py`
- [ ] 實現 `initialize_collections()` 方法
- [ ] 實現 `add_chapter_to_context()` 方法
- [ ] 測試向量數據庫基本操作

**Day 3-4: 檢索功能實現**
- [ ] 實現 `retrieve_global_context()` 方法
- [ ] 實現 `retrieve_volume_context()` 方法
- [ ] 實現 `build_chapter_context()` 組合上下文
- [ ] 測試檢索精度和速度

**Day 5-6: 上下文壓縮與優化**
- [ ] 實現 `compress_context()` 智能壓縮
- [ ] Token 計數集成（使用 tiktoken）
- [ ] 優化檢索策略（調整 top_k 參數）
- [ ] 性能測試: 100 章數據檢索延遲

**Day 7: NovelGenerator 集成**
- [ ] 修改 `generate_chapter()` 使用增強上下文
- [ ] 擴展 `build_chapter_prompt_phase2()`
- [ ] 端到端測試: 生成 10 章並驗證上下文傳遞
- [ ] 文檔更新

#### 里程碑驗收標準
- ✅ ChromaDB 成功存儲 100 章內容
- ✅ 全局檢索能找到 5 章前的角色設定
- ✅ 卷內檢索能找到本卷相關劇情
- ✅ 上下文壓縮後 Token 數 < 2000
- ✅ 生成章節時正確引用前文信息

#### 依賴關係
- **前置**: Phase 2.1 完成
- **並行**: Phase 2.3 可同步開發（獨立模組）
- **後置**: 性能優化

---

### Phase 2.3: 一致性檢查 (預計 3-5 天)

#### 任務列表

**Day 1-2: ConsistencyChecker 基礎**
- [ ] 創建 `core/consistency_checker.py`
- [ ] 實現 `track_character_state()` 方法
- [ ] 實現 `track_timeline()` 方法
- [ ] 實現 `track_world_setting()` 方法
- [ ] 單元測試: 追蹤功能

**Day 3-4: 檢查邏輯實現**
- [ ] 實現 `check_character_consistency()` 方法
- [ ] 實現 `check_timeline_consistency()` 方法
- [ ] 實現 `check_setting_consistency()` 方法
- [ ] 實現 `run_full_check()` 綜合檢查
- [ ] 測試案例: 故意引入矛盾驗證檢測

**Day 5: 集成與優化**
- [ ] 集成到 `NovelGenerator.generate_chapter()`
- [ ] 添加警告輸出到控制台
- [ ] 可選: 保存檢查日誌到 `logs/consistency_checks.log`
- [ ] 端到端測試

#### 里程碑驗收標準
- ✅ 能檢測到角色死亡後復活
- ✅ 能檢測到時間線倒流
- ✅ 能檢測到設定前後矛盾
- ✅ 檢查結果包含清晰的錯誤描述和建議
- ✅ 檢查延遲 < 3 秒

#### 依賴關係
- **前置**: Phase 2.2 完成（依賴 ContextManager 檢索）
- **並行**: 可與 Phase 2.2 並行開發
- **後置**: 無

---

### 實作時間線總覽

```
Week 1: Phase 2.1 - 分卷 + 章節大綱
├─ Day 1-2: VolumeManager 基礎
├─ Day 3-4: 提示詞擴展
├─ Day 5-6: NovelGenerator 集成
└─ Day 7: 測試與文檔

Week 2: Phase 2.2 - RAG + 雙層上下文
├─ Day 1-2: ChromaDB 集成
├─ Day 3-4: 檢索功能
├─ Day 5-6: 上下文壓縮
└─ Day 7: 集成測試

Week 3 (前半): Phase 2.3 - 一致性檢查
├─ Day 1-2: ConsistencyChecker 基礎
├─ Day 3-4: 檢查邏輯
└─ Day 5: 集成與優化

Week 3 (後半): 整合測試與優化
├─ Day 6: 100 章完整生成測試
└─ Day 7: 性能調優與文檔完善
```

---

## 8. 測試計劃

### 8.1 單元測試策略

#### 測試框架選擇
- 使用 `pytest` 作為測試框架
- 使用 `pytest-mock` 進行 API 調用模擬

#### 測試檔案結構
```
tests/
├── unit/
│   ├── test_volume_manager.py
│   ├── test_context_manager.py
│   ├── test_plot_manager.py
│   └── test_consistency_checker.py
├── integration/
│   ├── test_phase2_workflow.py
│   └── test_backward_compatibility.py
├── e2e/
│   └── test_full_generation.py
└── fixtures/
    ├── sample_outline.txt
    └── sample_chapters.json
```

#### 單元測試案例

**tests/unit/test_volume_manager.py**
```python
import pytest
from core.volume_manager import VolumeManager

def test_create_volume_plan_30_chapters():
    """測試 30 章的分卷規劃"""
    vm = VolumeManager(project_dir="test_project", ...)
    plan = vm.create_volume_plan(total_chapters=30, outline="...")

    assert plan['total_volumes'] == 2
    assert len(plan['volumes']) == 2
    assert plan['volumes'][0]['start_chapter'] == 1
    assert plan['volumes'][1]['end_chapter'] == 30

def test_create_volume_plan_100_chapters():
    """測試 100 章的分卷規劃"""
    vm = VolumeManager(project_dir="test_project", ...)
    plan = vm.create_volume_plan(total_chapters=100, outline="...")

    assert plan['total_volumes'] in [3, 4]
    # 驗證分卷連續性
    for i in range(len(plan['volumes']) - 1):
        assert plan['volumes'][i]['end_chapter'] + 1 == plan['volumes'][i+1]['start_chapter']

def test_get_volume_by_chapter():
    """測試根據章節號獲取分卷"""
    vm = VolumeManager(...)
    vm.volume_plan = {...}  # Mock 數據

    vol = vm.get_volume_by_chapter(15)
    assert vol['volume_id'] == 1
    assert vol['start_chapter'] <= 15 <= vol['end_chapter']
```

**tests/unit/test_context_manager.py**
```python
import pytest
from core.context_manager import ContextManager

@pytest.fixture
def context_mgr(tmp_path):
    """測試用 ContextManager 實例"""
    return ContextManager(project_dir=str(tmp_path))

def test_initialize_collections(context_mgr):
    """測試初始化向量庫"""
    context_mgr.initialize_collections()

    assert context_mgr.global_collection is not None
    assert context_mgr.volume_collection is not None

def test_add_and_retrieve_chapter(context_mgr):
    """測試添加和檢索章節"""
    context_mgr.initialize_collections()

    # 添加章節
    context_mgr.add_chapter_to_context(
        chapter_num=1,
        chapter_content="主角林宇是一名程序員...",
        volume_id=1,
        metadata={"characters": ["林宇"]}
    )

    # 檢索
    results = context_mgr.retrieve_global_context(
        query="林宇的職業",
        top_k=1
    )

    assert len(results) > 0
    assert "程序員" in results[0]['content']
```

**tests/unit/test_plot_manager.py**
```python
import pytest
from core.plot_manager import PlotManager, PlotPhase

def test_calculate_plot_phase():
    """測試劇情階段計算"""
    pm = PlotManager(project_dir="test_project")

    # 100 章小說
    assert pm.calculate_plot_phase(10, 100) == PlotPhase.INTRODUCTION  # 前 25%
    assert pm.calculate_plot_phase(50, 100) == PlotPhase.DEVELOPMENT   # 25-60%
    assert pm.calculate_plot_phase(75, 100) == PlotPhase.TWIST         # 60-85%
    assert pm.calculate_plot_phase(95, 100) == PlotPhase.RESOLUTION    # 85%+

def test_calculate_conflict_intensity():
    """測試衝突強度計算"""
    pm = PlotManager(...)

    intensity = pm.calculate_conflict_intensity(
        chapter_num=10,
        plot_phase=PlotPhase.INTRODUCTION,
        volume_arc="rising"
    )

    assert 0.3 <= intensity <= 0.5  # 起階段低強度
```

**tests/unit/test_consistency_checker.py**
```python
import pytest
from core.consistency_checker import ConsistencyChecker

def test_check_character_death_resurrection(tmp_path):
    """測試檢測角色復活矛盾"""
    cc = ConsistencyChecker(project_dir=str(tmp_path), ...)

    # 記錄角色死亡
    cc.track_character_state(
        chapter_num=10,
        character_name="導師",
        state_updates={"status": "deceased"}
    )

    # 檢查包含已死角色的章節
    warnings = cc.check_character_consistency(
        chapter_num=15,
        chapter_content="導師突然出現並說..."
    )

    assert len(warnings) > 0
    assert "導師" in warnings[0]['message']
    assert "已死亡" in warnings[0]['message']
```

---

### 8.2 整合測試案例

**tests/integration/test_phase2_workflow.py**
```python
import pytest
from core.generator import NovelGenerator

def test_phase2_full_workflow(tmp_path):
    """測試 Phase 2 完整流程"""
    # 初始化
    generator = NovelGenerator(
        api_key="test_key",
        enable_phase2=True
    )

    # 創建專案
    generator.create_project(
        title="測試小說",
        genre="科幻",
        theme="AI 覺醒",
        total_chapters=50
    )

    # 驗證 Phase 2 管理器已初始化
    assert generator.volume_manager is not None
    assert generator.context_manager is not None

    # 生成大綱（Mock API）
    with mock.patch.object(generator.api_client, 'generate'):
        generator.generate_outline()

    # 驗證分卷計劃
    assert generator.volume_manager.volume_plan is not None
    assert len(generator.volume_manager.volume_plan['volumes']) >= 2

    # 生成 3 章（Mock API）
    with mock.patch.object(generator.api_client, 'generate'):
        for i in range(1, 4):
            generator.generate_chapter(i)

    # 驗證上下文數據庫有內容
    results = generator.context_manager.retrieve_global_context("主角", top_k=1)
    assert len(results) > 0

def test_backward_compatibility():
    """測試向後兼容性 - Phase 1 模式"""
    generator = NovelGenerator(
        api_key="test_key",
        enable_phase2=False
    )

    generator.create_project(
        title="短篇測試",
        genre="言情",
        theme="校園戀愛",
        total_chapters=10
    )

    # 驗證 Phase 2 管理器未初始化
    assert generator.volume_manager is None
    assert generator.context_manager is None

    # 驗證 Phase 1 功能正常
    with mock.patch.object(generator.api_client, 'generate'):
        generator.generate_outline()
        generator.generate_chapter(1)

    assert os.path.exists(os.path.join(generator.project_dir, "chapter_001.txt"))
```

---

### 8.3 端到端測試場景

**tests/e2e/test_full_generation.py**
```python
import pytest
from core.generator import NovelGenerator

@pytest.mark.slow
def test_generate_50_chapters_with_phase2():
    """
    端到端測試: 生成 50 章小說（Phase 2 模式）

    驗證:
    1. 分卷規劃合理
    2. 章節大綱完整
    3. 上下文傳遞正確
    4. 一致性檢查通過
    5. 所有章節生成成功
    """
    generator = NovelGenerator(
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        enable_phase2=True
    )

    # 創建專案
    generator.create_project(
        title="E2E 測試小說",
        genre="科幻",
        theme="星際探索",
        total_chapters=50
    )

    # 生成大綱
    generator.generate_outline()

    # 驗證分卷計劃
    volume_plan = generator.volume_manager.volume_plan
    assert volume_plan['total_volumes'] in [2, 3]

    # 生成所有章節
    generator.generate_all_chapters()

    # 驗證文件存在
    for i in range(1, 51):
        chapter_file = os.path.join(
            generator.project_dir,
            f"chapter_{i:03d}.txt"
        )
        assert os.path.exists(chapter_file)

        # 驗證字數
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 2000 <= len(content) <= 4000  # 允許一定偏差

    # 驗證 ChromaDB 數據
    total_chunks = generator.context_manager.global_collection.count()
    assert total_chunks >= 50  # 至少每章一個文檔

    # 驗證一致性檢查日誌
    consistency_log = os.path.join(
        generator.project_dir,
        "logs/consistency_checks.log"
    )
    if os.path.exists(consistency_log):
        with open(consistency_log, 'r', encoding='utf-8') as f:
            logs = f.read()
            # 不應有嚴重錯誤
            assert "ERROR" not in logs

    # 合併章節
    generator.merge_chapters()

    # 驗證完整小說
    full_novel = os.path.join(generator.project_dir, "full_novel.txt")
    assert os.path.exists(full_novel)

    with open(full_novel, 'r', encoding='utf-8') as f:
        content = f.read()
        assert len(content) >= 100000  # 至少 10 萬字

@pytest.mark.slow
def test_generate_100_chapters_stress():
    """
    壓力測試: 生成 100 章小說

    驗證性能和穩定性
    """
    import time

    start_time = time.time()

    generator = NovelGenerator(
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        enable_phase2=True
    )

    generator.create_project(
        title="壓力測試小說",
        genre="玄幻",
        theme="修仙傳奇",
        total_chapters=100
    )

    generator.generate_outline()
    generator.generate_all_chapters()

    end_time = time.time()
    total_time = end_time - start_time

    # 性能要求: 平均 40 秒/章（包括 RAG 和檢查）
    avg_time_per_chapter = total_time / 100
    assert avg_time_per_chapter < 60, f"平均生成時間 {avg_time_per_chapter:.1f}s 超過預期"

    # 驗證成本
    stats = generator.get_statistics()
    total_cost = stats['api_statistics']['total_cost']
    assert total_cost < 0.50, f"成本 ¥{total_cost:.2f} 超過預算"
```

---

### 8.4 性能測試指標

| 測試項目 | 目標指標 | 測試方法 |
|---------|---------|---------|
| **章節生成速度** | < 40 秒/章 | 生成 10 章測試,計算平均時間 |
| **RAG 檢索延遲** | < 1 秒 | 100 章數據庫,執行 10 次檢索 |
| **一致性檢查延遲** | < 3 秒 | 100 章歷史,檢查新章節 |
| **內存佔用** | < 2GB | 100 章生成過程監控 |
| **向量庫大小** | < 500MB | 100 章存儲後檢查 |
| **總成本** | < ¥0.30/100章 | API 成本追蹤 |

#### 性能測試腳本

**tests/performance/test_performance.py**
```python
import pytest
import time
import psutil
import os

def test_rag_retrieval_speed():
    """測試 RAG 檢索速度"""
    # 準備: 插入 100 章數據
    context_mgr = ContextManager(...)
    context_mgr.initialize_collections()

    for i in range(1, 101):
        context_mgr.add_chapter_to_context(
            chapter_num=i,
            chapter_content=f"第 {i} 章內容..." * 100,  # 模擬 3000 字
            volume_id=(i-1)//30 + 1,
            metadata={}
        )

    # 測試檢索速度
    queries = ["主角", "敵人", "寶物", "修煉", "戰鬥"]
    times = []

    for query in queries:
        start = time.time()
        results = context_mgr.retrieve_global_context(query, top_k=5)
        end = time.time()
        times.append(end - start)

    avg_time = sum(times) / len(times)
    assert avg_time < 1.0, f"平均檢索時間 {avg_time:.2f}s 超過 1 秒"

def test_memory_usage():
    """測試內存佔用"""
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    # 生成 20 章
    generator = NovelGenerator(...)
    # ... 生成邏輯 ...

    mem_after = process.memory_info().rss / 1024 / 1024
    mem_increase = mem_after - mem_before

    assert mem_increase < 500, f"內存增長 {mem_increase:.1f}MB 超過預期"
```

---

## 9. 技術選型與依賴

### 9.1 新增依賴項

**requirements_phase2.txt**
```txt
# Phase 1 依賴（現有）
requests>=2.31.0
python-dotenv>=1.0.0

# Phase 2 新增依賴
chromadb>=0.4.18              # 向量數據庫
sentence-transformers>=2.2.2  # 嵌入模型
tiktoken>=0.5.1              # Token 計數（OpenAI 官方）
```

### 9.2 技術選型理由

#### ChromaDB vs 其他向量數據庫

| 數據庫 | 優勢 | 劣勢 | 選擇理由 |
|-------|------|------|---------|
| **ChromaDB** ✅ | 嵌入式,無需服務器,Python 原生 | 不適合超大規模 | 適合單機部署,簡化架構 |
| Pinecone | 雲服務,性能強 | 需聯網,付費 | 增加依賴複雜度 |
| Milvus | 高性能,可擴展 | 部署複雜,需 Docker | 過度工程 |
| FAISS | 速度快 | 無持久化,需自己管理 | 缺乏便利性 |

#### 嵌入模型選擇

| 模型 | 大小 | 速度 | 精度 | 選擇理由 |
|------|------|------|------|---------|
| **all-MiniLM-L6-v2** ✅ | 80MB | 快 | 中等 | 平衡性能與精度 |
| all-mpnet-base-v2 | 420MB | 中 | 高 | 文件過大 |
| multilingual-e5-small | 118MB | 快 | 中 | 中文支援好,備選方案 |

#### Token 計數工具

使用 `tiktoken` 而非自己實現:
- OpenAI 官方工具,準確度高
- 支援多種模型 tokenizer
- 性能優化好

### 9.3 可選依賴

```txt
# 開發與測試
pytest>=7.4.0
pytest-mock>=3.11.1
pytest-cov>=4.1.0

# 性能監控
psutil>=5.9.5

# 日誌增強（可選）
loguru>=0.7.0
```

---

## 10. 性能與擴展性

### 10.1 性能優化策略

#### 向量數據庫優化
```python
# 批量插入優化
def add_chapters_batch(self, chapters: List[Dict]):
    """批量添加章節,減少 I/O"""
    documents = []
    metadatas = []
    ids = []

    for ch in chapters:
        documents.append(ch['content'])
        metadatas.append(ch['metadata'])
        ids.append(f"chapter_{ch['num']}")

    self.global_collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

# 使用本地嵌入模型（避免 API 調用）
embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
    device="cpu"  # 或 "cuda" if GPU 可用
)
```

#### 上下文緩存策略
```python
from functools import lru_cache

class ContextManager:
    @lru_cache(maxsize=50)
    def retrieve_global_context(self, query: str, top_k: int = 3):
        """緩存常見查詢結果"""
        # ... 檢索邏輯
        pass
```

#### 並行化生成（可選,未來優化）
```python
from concurrent.futures import ThreadPoolExecutor

def generate_chapters_parallel(self, chapter_range: range):
    """並行生成多個章節（需處理上下文依賴）"""
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(self._generate_chapter_async, i)
            for i in chapter_range
        ]
        # ... 處理結果
```

### 10.2 擴展性設計

#### 支援更大規模（500+ 章）

**分層向量庫**
```python
# 每 100 章創建一個獨立 Collection
collection_name = f"chapters_{(chapter_num-1)//100 * 100 + 1}_{min(chapter_num//100 * 100 + 100, total_chapters)}"
```

**增量索引**
```python
# 定期重建索引以優化性能
def rebuild_index_if_needed(self):
    if self.global_collection.count() % 100 == 0:
        # 觸發重建索引邏輯
        pass
```

#### 多語言支援（未來擴展）
```python
# 根據語言選擇嵌入模型
EMBEDDING_MODELS = {
    'zh': 'shibing624/text2vec-base-chinese',
    'en': 'all-MiniLM-L6-v2',
    'multi': 'multilingual-e5-small'
}

def __init__(self, language='zh'):
    model = EMBEDDING_MODELS.get(language, 'all-MiniLM-L6-v2')
    self.embedding_function = SentenceTransformerEmbeddingFunction(model)
```

### 10.3 資源限制處理

#### Token 限制策略
```python
MAX_CONTEXT_TOKENS = 2000
MAX_GENERATION_TOKENS = 5000

def build_chapter_context(self, ...):
    context = self._retrieve_all_context(...)

    # Token 計數
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(context)

    if len(tokens) > MAX_CONTEXT_TOKENS:
        # 智能壓縮
        context = self.compress_context(context, MAX_CONTEXT_TOKENS)

    return context
```

#### 磁盤空間管理
```python
# 定期清理舊分卷的詳細上下文
def cleanup_old_volume_context(self, current_volume: int):
    """清理 2 個分卷之前的詳細上下文"""
    if current_volume > 2:
        old_volume = current_volume - 2
        self.chroma_client.delete_collection(f"volume_{old_volume}_context")
```

---

## 結論

本架構設計為 AI 小說生成器 Phase 2 提供了完整的技術藍圖:

### 核心優勢
1. **向後兼容**: enable_phase2 標誌確保 MVP 功能不受影響
2. **模組化**: 四大管理器職責清晰,可獨立測試和優化
3. **可擴展**: 支援從 30 章到 100+ 章的靈活擴展
4. **高效能**: RAG 檢索 + 智能壓縮,保證生成質量

### 實作路徑清晰
- Phase 2.1: 分卷管理（1 週）
- Phase 2.2: RAG 上下文（1 週）
- Phase 2.3: 一致性檢查（3-5 天）

### 質量保證
- 完整的單元測試、整合測試、端到端測試
- 明確的性能指標和驗收標準
- 詳細的技術文檔和使用範例

**開發團隊可以直接基於此文檔開始實作,預計 2.5-3 週完成 Phase 2 全部功能。**

---

*文檔版本: 1.0*
*最後更新: 2026-01-04*
*審核狀態: 待開發驗證*
